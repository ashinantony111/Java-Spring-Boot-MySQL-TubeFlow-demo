import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, asc, or_, and_, func
from app.models import (
    User, Channel, Category, Video, Comment,
    VideoReaction, CommentReaction, Subscription,
    Playlist, PlaylistItem, WatchHistory, WatchLater
)

def now_utc():
    return datetime.datetime.now(datetime.timezone.utc)

# --- Users & Channels ---
def get_all_users(db: Session) -> List[User]:
    return db.query(User).options(joinedload(User.channel)).all()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).options(joinedload(User.channel)).filter(User.id == user_id).first()

def get_channel_by_id(db: Session, channel_id: int) -> Optional[Channel]:
    return db.query(Channel).options(joinedload(Channel.user)).filter(Channel.id == channel_id).first()

def get_channel_by_handle(db: Session, handle: str) -> Optional[Channel]:
    return db.query(Channel).options(joinedload(Channel.user)).filter(Channel.handle == handle).first()

def get_categories(db: Session) -> List[Category]:
    return db.query(Category).order_by(Category.id).all()

# --- Videos ---
def get_videos(
    db: Session,
    category_slug: Optional[str] = None,
    search_query: Optional[str] = None,
    sort_by: str = "recent",
    limit: int = 50,
    offset: int = 0
) -> List[Video]:
    q = db.query(Video).options(
        joinedload(Video.channel),
        joinedload(Video.category)
    ).filter(Video.visibility == "public")

    if category_slug and category_slug != "all":
        q = q.join(Video.category).filter(Category.slug == category_slug)

    if search_query:
        search_filter = f"%{search_query.strip()}%"
        q = q.join(Video.channel).filter(
            or_(
                Video.title.ilike(search_filter),
                Video.description.ilike(search_filter),
                Video.tags.ilike(search_filter),
                Channel.channel_name.ilike(search_filter)
            )
        )

    if sort_by == "popular":
        q = q.order_by(desc(Video.views_count))
    elif sort_by == "likes":
        q = q.order_by(desc(Video.likes_count))
    elif sort_by == "oldest":
        q = q.order_by(asc(Video.created_at))
    else:  # recent
        q = q.order_by(desc(Video.created_at))

    return q.offset(offset).limit(limit).all()

def get_video_by_id(db: Session, video_id: int) -> Optional[Video]:
    return db.query(Video).options(
        joinedload(Video.channel).joinedload(Channel.user),
        joinedload(Video.category)
    ).filter(Video.id == video_id).first()

def increment_views(db: Session, video_id: int) -> int:
    video = db.query(Video).filter(Video.id == video_id).first()
    if video:
        video.views_count = (video.views_count or 0) + 1
        db.commit()
        return video.views_count
    return 0

def create_video(
    db: Session,
    channel_id: int,
    title: str,
    description: str,
    video_url: str,
    thumbnail_url: str,
    duration: str = "0:00",
    duration_seconds: int = 0,
    category_id: Optional[int] = None,
    tags: str = "",
    visibility: str = "public"
) -> Video:
    video = Video(
        channel_id=channel_id,
        title=title,
        description=description,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        duration=duration,
        duration_seconds=duration_seconds,
        category_id=category_id,
        tags=tags,
        visibility=visibility,
        created_at=now_utc()
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return video

# --- Comments ---
def get_comments(db: Session, video_id: int) -> List[Comment]:
    return db.query(Comment).options(
        joinedload(Comment.user)
    ).filter(Comment.video_id == video_id).order_by(desc(Comment.created_at)).all()

def add_comment(db: Session, video_id: int, user_id: int, content: str, parent_id: Optional[int] = None) -> Comment:
    comment = Comment(
        video_id=video_id,
        user_id=user_id,
        parent_id=parent_id,
        content=content,
        likes_count=0,
        created_at=now_utc()
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def delete_comment(db: Session, comment_id: int, user_id: int) -> bool:
    comment = db.query(Comment).filter(Comment.id == comment_id, Comment.user_id == user_id).first()
    if comment:
        db.delete(comment)
        db.commit()
        return True
    return False

# --- Reactions (Like / Dislike) ---
def react_to_video(db: Session, video_id: int, user_id: int, reaction_type: str) -> Dict[str, Any]:
    existing = db.query(VideoReaction).filter(
        VideoReaction.video_id == video_id,
        VideoReaction.user_id == user_id
    ).first()

    video = db.query(Video).filter(Video.id == video_id).first()
    if not video:
        return {"likes": 0, "dislikes": 0, "current": None}

    if existing:
        if existing.reaction_type == reaction_type:
            # Toggle off
            db.delete(existing)
            if reaction_type == "like":
                video.likes_count = max(0, video.likes_count - 1)
            else:
                video.dislikes_count = max(0, video.dislikes_count - 1)
            current_reaction = None
        else:
            # Change from like to dislike or vice versa
            old_type = existing.reaction_type
            existing.reaction_type = reaction_type
            if old_type == "like":
                video.likes_count = max(0, video.likes_count - 1)
                video.dislikes_count = video.dislikes_count + 1
            else:
                video.dislikes_count = max(0, video.dislikes_count - 1)
                video.likes_count = video.likes_count + 1
            current_reaction = reaction_type
    else:
        # New reaction
        new_reaction = VideoReaction(video_id=video_id, user_id=user_id, reaction_type=reaction_type)
        db.add(new_reaction)
        if reaction_type == "like":
            video.likes_count = video.likes_count + 1
        else:
            video.dislikes_count = video.dislikes_count + 1
        current_reaction = reaction_type

    db.commit()
    return {
        "likes": video.likes_count,
        "dislikes": video.dislikes_count,
        "current": current_reaction
    }

def get_user_video_reaction(db: Session, video_id: int, user_id: int) -> Optional[str]:
    reaction = db.query(VideoReaction).filter(
        VideoReaction.video_id == video_id,
        VideoReaction.user_id == user_id
    ).first()
    return reaction.reaction_type if reaction else None

# --- Subscriptions ---
def is_subscribed(db: Session, user_id: int, channel_id: int) -> bool:
    return db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.channel_id == channel_id
    ).first() is not None

def toggle_subscription(db: Session, user_id: int, channel_id: int) -> Dict[str, Any]:
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        return {"subscribed": False, "subscribers": 0}

    sub = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.channel_id == channel_id
    ).first()

    if sub:
        db.delete(sub)
        channel.subscriber_count = max(0, channel.subscriber_count - 1)
        subscribed = False
    else:
        new_sub = Subscription(user_id=user_id, channel_id=channel_id)
        db.add(new_sub)
        channel.subscriber_count = channel.subscriber_count + 1
        subscribed = True

    db.commit()
    return {"subscribed": subscribed, "subscribers": channel.subscriber_count}

def get_user_subscriptions(db: Session, user_id: int) -> List[Channel]:
    return db.query(Channel).join(Subscription).filter(Subscription.user_id == user_id).all()

def get_subscriptions_videos(db: Session, user_id: int) -> List[Video]:
    return db.query(Video).options(
        joinedload(Video.channel),
        joinedload(Video.category)
    ).join(Channel, Video.channel_id == Channel.id)\
     .join(Subscription, Subscription.channel_id == Channel.id)\
     .filter(Subscription.user_id == user_id)\
     .order_by(desc(Video.created_at))\
     .all()

# --- History & Watch Later ---
def record_watch_history(db: Session, user_id: int, video_id: int, progress_seconds: int = 0):
    entry = db.query(WatchHistory).filter(
        WatchHistory.user_id == user_id,
        WatchHistory.video_id == video_id
    ).first()

    if entry:
        entry.watched_at = now_utc()
        entry.progress_seconds = progress_seconds
    else:
        entry = WatchHistory(
            user_id=user_id,
            video_id=video_id,
            progress_seconds=progress_seconds,
            watched_at=now_utc()
        )
        db.add(entry)
    db.commit()

def get_watch_history(db: Session, user_id: int) -> List[Dict[str, Any]]:
    rows = db.query(WatchHistory).options(
        joinedload(WatchHistory.video).joinedload(Video.channel)
    ).filter(WatchHistory.user_id == user_id).order_by(desc(WatchHistory.watched_at)).all()

    return [{"history": r, "video": r.video} for r in rows if r.video]

def clear_watch_history(db: Session, user_id: int):
    db.query(WatchHistory).filter(WatchHistory.user_id == user_id).delete()
    db.commit()

def toggle_watch_later(db: Session, user_id: int, video_id: int) -> bool:
    item = db.query(WatchLater).filter(
        WatchLater.user_id == user_id,
        WatchLater.video_id == video_id
    ).first()

    if item:
        db.delete(item)
        saved = False
    else:
        db.add(WatchLater(user_id=user_id, video_id=video_id))
        saved = True

    db.commit()
    return saved

def is_watch_later(db: Session, user_id: int, video_id: int) -> bool:
    return db.query(WatchLater).filter(
        WatchLater.user_id == user_id,
        WatchLater.video_id == video_id
    ).first() is not None

def get_watch_later_videos(db: Session, user_id: int) -> List[Video]:
    rows = db.query(WatchLater).options(
        joinedload(WatchLater.video).joinedload(Video.channel)
    ).filter(WatchLater.user_id == user_id).order_by(desc(WatchLater.added_at)).all()
    return [r.video for r in rows if r.video]

def get_liked_videos(db: Session, user_id: int) -> List[Video]:
    return db.query(Video).options(
        joinedload(Video.channel)
    ).join(VideoReaction, Video.id == VideoReaction.video_id)\
     .filter(VideoReaction.user_id == user_id, VideoReaction.reaction_type == "like")\
     .order_by(desc(VideoReaction.created_at))\
     .all()
