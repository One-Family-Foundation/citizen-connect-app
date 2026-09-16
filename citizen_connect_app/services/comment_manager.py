import frappe

from samaaja.utils.result import Result
from citizen_connect_app.utils.error_logger import ErrorLogger
from citizen_connect_app.utils.commons import create_media_url


def create_comment(post_id: str, comment_text: str) -> Result:
    try:
        if frappe.session.user == "Guest":
            return Result.unauthorized("Please login to comment")

        user_id = frappe.session.user

        if not post_id or not post_id.strip():
            return Result.bad_request("Post ID is required")

        if not frappe.db.exists("Post", post_id):
            return Result.bad_request("Post not found")

        if not comment_text or not comment_text.strip():
            return Result.bad_request("Comment cannot be blank")

        comment = frappe.new_doc("Community Comment")
        comment.post_id = post_id
        comment.user_id = user_id
        comment.comment = comment_text.strip()

        comment.save(ignore_permissions=True)

        return Result.success(
            "Comment created successfully",
            data=comment
        )

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            "Failed to create comment",
            error_data=str(e)
        )

def get_comments(post_id: str, limit=10, offset=0) -> Result:
    try:
        # Check if post exists
        if not post_id or not post_id.strip():
            return Result.bad_request("Post ID is required")

        if not frappe.db.exists("Post", post_id):
            return Result.bad_request("Post not found")

        # Validate pagination
        try:
            limit = int(limit)
            offset = int(offset)
        except (TypeError, ValueError):
            return Result.bad_request("Limit and offset must be valid numbers")

        if limit <= 0:
            return Result.bad_request("Limit must be greater than 0")

        if offset < 0:
            return Result.bad_request("Offset cannot be negative")

        comments = frappe.db.sql(
            """
            SELECT
                c.name,
                c.comment,
                c.user_id,
                c.creation,
                u.first_name as full_name,
                u.user_image
            FROM `tabCommunity Comment` c
            LEFT JOIN `tabUser` u
                ON c.user_id = u.name
            WHERE c.post_id = %s
            ORDER BY c.creation DESC
            LIMIT %s OFFSET %s
            """,
            (post_id, limit, offset),
            as_dict=True,
        )
        for comment in comments:
            if comment.get("user_image"):
                comment["user_image"] = create_media_url(
                    comment["user_image"]
                )


        return Result.success(
            "Comments retrieved successfully",
            data={
                "comments": comments,
                "limit": limit,
                "offset": offset,
                "has_more": len(comments) == limit,
            },
        )

    except Exception as e:
        ErrorLogger.log(e)
        return Result.failure(
            "Failed to fetch comments",
            error_data=str(e)
        )