from typing import Any, Mapping

from app.domain.entities.likes import Like


def convert_like_document_to_entity(like_document: Mapping[str, Any]) -> Like:
    return Like(
        oid=like_document['oid'],
        user_id=like_document['user_id'],
        liked_by_user_id=like_document['liked_by_user_id'],
        creation_date=like_document['creation_date'],
        is_viewed_by_liked_user=like_document['is_viewed_by_liked_user'],
        status=like_document['status'],
    )

def convert_like_entity_to_document(like: Like) -> dict:
    return {
        'oid': like.oid,
        'user_id': like.user_id,
        'liked_by_user_id': like.liked_by_user_id,
        'creation_date': like.created_at,
        'is_viewed_by_liked_user': like.is_viewed_by_liked_user,
        'status': like.status,
    }