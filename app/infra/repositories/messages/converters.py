import datetime
from typing import (
    Any,
    Mapping,
)

from app.domain.entities.likes import Like
from app.domain.entities.messages import (
    Chat,
    ChatParticipants,
    # ChatListener,
    Message,
)
from app.domain.values.messages import (
    Text,
    Title,
)


def convert_message_entity_to_document(message: Message) -> dict:
    return {
        'oid': message.oid,
        'text': message.text.as_generic_type(),
        'sent_at': message.created_at,
        'chat_oid': message.chat_oid,
        'sender_id' : message.sender_id,
        'recipient_id': message.recipient_id,
        'read_by_recipient': message.read_by_recipient,
        'visibility_sender': message.visibility_sender,
        'visibility_recipient': message.visibility_recipient,
        'visibility_all': message.visibility_all,

    }


# def convert_chat_entity_to_document(chat: Chat) -> dict:
#     return {
#         'oid': chat.oid,
#         'title': chat.title.as_generic_type(),
#         'created_at': chat.created_at,
#     }

def convert_chat_entity_to_document(chat: Chat) -> dict:
    print(f'{chat.participants}')
    return {
        'oid': chat.oid,
        'created_at': chat.created_at,
        'updated_at': chat.updated_at,
        'delete_by_first': chat.delete_by_first,
        "delete_by_second": chat.delete_by_second,
        'participants':list(chat.participants),
        'last_message': list(chat.last_message) if chat.last_message else None

        }

def convert_message_document_to_entity(message_document: Mapping[str, Any]) -> Message:
    return Message(
        text=Text(value=message_document['text']),
        oid=message_document['oid'],
        sent_at=message_document['sent_at'],
        chat_oid=message_document['chat_oid'],
        sender_id=message_document['sender_id'],
        recipient_id=message_document['recipient_id'],
        read_by_recipient=message_document['read_by_recipient'],
        visibility_sender=message_document['visibility_sender'],
        visibility_recipient=message_document['visibility_recipient'],
    )


def convert_chat_participants_document_to_entity(user_id: int) -> ChatParticipants:
    # TODO: принимать сущность слушателя
    return ChatParticipants(user_id=user_id)


def convert_chat_messages_document_to_entity(chat_oid: str, text: Text, 
                                             sender_id: int,
                                             recipient_id: int,
                                             sent_at: datetime,
                                             read_by_recipient: bool,
                                             visibility_sender: bool,
                                             visibility_recipient: bool,
                                             visibility_all: bool) -> Message:
    # TODO: принимать сущность сообщения
    return Message(
        chat_oid=chat_oid,
        sender_id=sender_id,
        recipient_id=recipient_id,
        sent_at=sent_at,
        read_by_recipient=read_by_recipient,
        visibility_sender=visibility_sender,
        visibility_recipient=visibility_recipient,
        visibility_all=visibility_all,
    )


def convert_chat_document_to_entity(chat_document: Mapping[str, Any]) -> Chat:
    # print(f'{chat_document=}')
    return Chat(
        oid=chat_document['oid'],
        # last_messages={
        #     convert_chat_messages_document_to_entity(chat_oid,text=text,sender_id=sender_id,
        #                                              recipient_id=recipient_id,
        #                                              sent_at=sent_at,
        #                                              read_by_recipient=read_by_recipient,
        #                                              visibility_sender=visibility_sender,
        #                                              visibility_recipient=visibility_recipient,
        #                                              visibility_all=visibility_all)
        #     for chat_oid, text,sender_id,recipient_id,sent_at,
        #     read_by_recipient,visibility_sender,visibility_recipient,visibility_all  in chat_document.get('last_messages', [])
        # },
        # is_deleted=chat_document['is_deleted'],
        last_message=chat_document.get('last_message') if chat_document.get('last_message') is not None else None,
        delete_by_first=chat_document['delete_by_first'],
        created_at = chat_document['created_at'],
        updated_at = chat_document['updated_at'] ,
        delete_by_second=chat_document['delete_by_second'],
        participants={
            convert_chat_participants_document_to_entity(user_id=user_id)
            for user_id in chat_document.get('participants', [])
        },
    )
