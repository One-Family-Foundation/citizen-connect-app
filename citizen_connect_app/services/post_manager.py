import frappe
from samaaja.utils.result import Result
from citizen_connect_app.utils.error_logger import ErrorLogger
from citizen_connect_app.models.post import Post, PostResponse , MediaResponse
from citizen_connect_app.models.utils import Location
from pydantic import ValidationError
from citizen_connect_app.utils.commons  import resolve_location,create_media_url
from citizen_connect_app.services.user import UserManager

logger = frappe.logger(
    "citizen_connect_app",
    allow_site=True,
    file_count=50
)

logger.setLevel("DEBUG")

MIN_LIMIT = 1
MAX_LIMIT = 100
DEFAULT_LIMIT = 10
DEFAULT_OFFSET = 0

def create_post(post_data: dict) -> Result:
    try:
        if frappe.session.user == "Guest":
            return Result.bad_request(message="User must be logged in to create a post.")
        try:
            post = Post(**post_data)
        except ValidationError as e:
            messages = [
                f"{'.'.join(map(str, err['loc']))}: {err['msg']}"
                for err in e.errors()
            ]
            return Result.bad_request(message="; ".join(messages))
        saved_files = []
        for file in post.files:
            saved_file = frappe.get_doc({
                "doctype": "File",
                "file_name": file.filename,
                "content": file.read(),
                "is_private": 0,
            }).insert(ignore_permissions=True)
            saved_files.append({
                "doctype": "Media",
                "media": saved_file.file_url
            })
        
        location = Location()
        if post.location:
            location_result = resolve_location(post.location)
            if location_result.is_bad_request:
                return location_result
            location.country = location_result.data.country
            location.geo1 = location_result.data.geo1
            location.geo2 = location_result.data.geo2
        doc = frappe.get_doc({
            "doctype": "Post",
            "description": post.description,
            "country": location.country,
            "geography_l1": location.geo1,
            "geography_l2": location.geo2 ,
            "category_l1": post.category.l1,
            "user": frappe.session.user,
            "media": saved_files,
        }).insert(ignore_permissions=True)
        logger.info(f"Post created with ID: {doc.name}")
        return Result.success(message="Post created successfully.", data=doc.as_dict())
    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(message="Failed to create post.", data={"error": str(e)}, error_data={"traceback": frappe.get_traceback()})

def get_list(
    limit=DEFAULT_LIMIT,
    offset=DEFAULT_OFFSET,
    category_l1=None,
    country=None,
    geography_l1=None,
    geography_l2=None,
    lang="en"
) -> Result:
    try:
        limit = max(MIN_LIMIT, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))
        where_clause, values = build_filters(
            category_l1=category_l1,
            country=country,
            geography_l1=geography_l1,
            geography_l2=geography_l2,
        )


        query = f"""
            SELECT
                p.name AS id,
                p.description,
                p.user,
                p.creation,
                p.modified,

                c.country_name AS country,
                g1.geo_l1 AS geography_l1,
                g2.geo_2 AS geography_l2,
                p.category_l1

            FROM `tabPost` p

            LEFT JOIN `tabCountry` c
                ON c.name = p.country

            LEFT JOIN `tabGeography L1` g1
                ON g1.name = p.geography_l1

            LEFT JOIN `tabGeography L2` g2
                ON g2.name = p.geography_l2
               {where_clause}

            ORDER BY p.creation DESC
            LIMIT %s OFFSET %s
        """

        values.extend([limit, offset])
        media_base_url = frappe.utils.get_url()
        post_rows = frappe.db.sql(query, tuple(values) , as_dict=True)

        post_ids = [post["id"] for post in post_rows]

        media_map = {}

        if post_ids:
            media_rows = frappe.get_all(
                "Media",
                filters={
                    "parent": ["in", post_ids],
                    "parenttype": "Post",
                    "parentfield": "media",
                },
                fields=["parent", "media", "caption"],
            )

            for row in media_rows:
                media_url = create_media_url(row.media)

                media_map.setdefault(row.parent, []).append({
                    "media": media_url,
                    "caption": row.caption,
                })    

        for post in post_rows:
            post["media"] = media_map.get(post["id"], [])
        
        user_summaries = UserManager.get_user_summaries([post["user"] for post in post_rows], lang=lang)
        
        user_summaries_by_email = {user.email: user for user in user_summaries}

        posts = []

        for row in post_rows:
            data = {
                **row,
                "location": {
                    "country": {"name": row["country"]} if row["country"] else None,
                    "geo1": {"name": row["geography_l1"]} if row["geography_l1"] else None,
                    "geo2": {"name": row["geography_l2"]} if row["geography_l2"] else None,
                },
                "category": {
                    "l1": {"name": row["category_l1"]} if row["category_l1"] else None,
                    "l2": None,
                },
                "user": user_summaries_by_email.get(row["user"]),
            }

            posts.append(
                PostResponse.model_validate(data,context={"lang": lang}).model_dump()
            )
        return Result.success(
            message="Posts fetched successfully.",
            data=posts,
        )

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            message="Failed to get post list.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )

def delete_post(post_id: str) -> Result:
    try:
        if frappe.session.user == "Guest":
            return Result.bad_request(
                message="User must be logged in to delete a post."
            )

        if not post_id:
            return Result.bad_request(
                message="post_id is required."
            )

        post = frappe.db.get_value(
            "Post",
            post_id,
            ["name", "user"],
            as_dict=True
        )

        if not post:
            return Result.bad_request(
                message="Post not found."
            )

        if post.user != frappe.session.user:
            return Result.bad_request(
                message="You can only delete your own post."
            )

        media_rows = frappe.get_all(
            "Media",
            filters={
                "parent": post_id,
                "parenttype": "Post",
                "parentfield": "media",
            },
            fields=["name", "media"],
        )

        for media in media_rows:
            if media.media:
                file_name = frappe.db.get_value(
                    "File",
                    {"file_url": media.media},
                    "name"
                )

                if file_name:
                    frappe.delete_doc(
                        "File",
                        file_name,
                        ignore_permissions=True
                    )

        frappe.delete_doc(
            "Post",
            post_id,
            ignore_permissions=True
        )

        logger.info(
            f"Post {post_id} deleted by user {frappe.session.user}"
        )

        return Result.success(
            message="Post deleted successfully.",
            data={"post_id": post_id}
        )

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            message="Failed to delete post.",
            data={"error": str(e)},
            error_data={
                "traceback": frappe.get_traceback()
            }
        )

def like_post(post_id: str) -> Result:
    try:
        if frappe.session.user == "Guest":
            return Result.bad_request(
                message="User must be logged in to like a post."
            )

        if not post_id:
            return Result.bad_request(
                message="post_id is required."
            )

        if not frappe.db.exists("Post", post_id):
            return Result.bad_request(
                message="Post not found."
            )

        user_id = frappe.session.user

        existing_like = frappe.db.get_value(
            "Post Like",
            {
                "post_id": post_id,
                "user_id": user_id
            },
            "name"
        )

        if existing_like:
            frappe.delete_doc(
                "Post Like",
                existing_like,
                ignore_permissions=True
            )

            logger.info(
                f"Post {post_id} disliked by user {user_id}"
            )

            return Result.success(
                message="Post disliked successfully.",
                data={
                    "post_id": post_id,
                    "user_id": user_id,
                    "liked": False
                }
            )

        like = frappe.get_doc({
            "doctype": "Post Like",
            "post_id": post_id,
            "user_id": user_id
        })

        like.insert(ignore_permissions=True)

        logger.info(
            f"Post {post_id} liked by user {user_id}"
        )

        return Result.success(
            message="Post liked successfully.",
            data={
                "post_id": post_id,
                "user_id": user_id,
                "liked": True,
                "like_id": like.name
            }
        )

    except Exception as e:
        ErrorLogger.log(e)

        return Result.failure(
            message="Failed to like/dislike post.",
            data={"error": str(e)},
            error_data={
                "traceback": frappe.get_traceback()
            }
        )        

def build_filters(
    category_l1=None,
    country=None,
    geography_l1=None,
    geography_l2=None,
):
    conditions = []
    values = []

    if category_l1:
        conditions.append("p.category_l1 = %s")
        values.append(category_l1)

    if country:
        conditions.append("p.country = %s")
        values.append(country)

    if geography_l1:
        conditions.append("g1.geo_l1 = %s")
        values.append(geography_l1)

    if geography_l2:
        conditions.append("g2.geo_2 = %s")
        values.append(geography_l2)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    return where_clause, values  

def count_user_post(user_id: str) -> Result:
    post_count = frappe.db.count(
        "Post",
        {
            "user": user_id
        }
    )

    return Result.success(
        message="Post count fetched successfully.",
        data=post_count,
    )
def get_user_post(
    user_id: str,
    limit=DEFAULT_LIMIT,
    offset=DEFAULT_OFFSET,
) -> Result:
    try:
        if not user_id:
            return Result.bad_request(
                message="user_id is required."
            )

        limit = max(MIN_LIMIT, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))

        posts = frappe.get_all(
            "Post",
            filters={
                "user": user_id,
            },
            fields=[
                "description",
                "creation",
            ],
            order_by="creation DESC",
            limit_page_length=limit,
            limit_start=offset,
        )

        return Result.success(
            message="User posts fetched successfully.",
            data=posts,
        )

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            message="Failed to get user posts.",
            data={"error": str(e)},
            error_data={"traceback": frappe.get_traceback()},
        )
