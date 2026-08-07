import frappe
from samaaja.utils.result import Result
from citizen_connect_app.utils.error_logger import ErrorLogger
from citizen_connect_app.models.post import Post, PostResponse
from citizen_connect_app.models.utils import Location
from pydantic import ValidationError
from citizen_connect_app.utils.commons  import resolve_location

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
                "is_private": 1,
            }).insert(ignore_permissions=True)
            saved_files.append({
                "doctype": "Post Media",
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
            "category_l1": post.category.l1 if post.category else None,
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
) -> Result:
    try:
        limit = max(MIN_LIMIT, min(int(limit), MAX_LIMIT))
        offset = max(0, int(offset))

        query = f"""
                SELECT
                p.name as id,
                p.description,
                p.country,
                p.geography_l1,
                p.geography_l2,
                p.category_l1,
                p.user,
                p.creation,
                p.modified
            FROM `tabPost` p
            ORDER BY p.creation DESC
            LIMIT %s OFFSET %s
        """

        post_rows = frappe.db.sql(query, (limit, offset), as_dict=True)

        posts = [PostResponse(**row).model_dump() for row in post_rows]
        return Result.success(data=posts)

    except Exception as e:
        ErrorLogger.log(frappe.get_traceback(), "Get post list failed")
        return Result.failure(message="Failed to get post list.", data={"error": str(e)}, error_data={"traceback": frappe.get_traceback()})
