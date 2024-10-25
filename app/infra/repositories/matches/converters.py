# def convert_like_document_to_entity(like_document: Mapping[str, Any]) -> Like:
#     return Like(
#         oid=like_document['oid'],
#         user_id=like_document['user_id'],
#         liked_by_user_id=like_document['liked_by_user_id'],
#         creation_date=like_document['creation_date'],
#         is_viewed_by_liked_user=like_document['is_viewed_by_liked_user'],
#         status=like_document['status'],
#     )

from app.domain.entities.matches import Match


def convert_match_entity_to_document(match: Match) -> dict:
    return {
        'oid': match.oid,
        'user_id': match.user_id,
        'liked_by_user_id': match.liked_by_user_id,
        'is_viewed_by_user': match.is_viewed_by_user,
        'is_viewed_by_liked_user': match.is_viewed_by_liked_user,
        'creation_date': match.created_at
    }