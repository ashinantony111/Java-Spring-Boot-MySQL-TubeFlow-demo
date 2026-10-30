import datetime
from sqlalchemy.orm import Session
from app.models import (
    Base, User, Channel, Category, Video, Comment,
    Subscription, VideoReaction, Playlist, PlaylistItem, WatchHistory
)

def seed_database(db: Session, engine=None):
    bind_engine = engine or db.get_bind()
    # Ensure tables are created
    Base.metadata.create_all(bind=bind_engine)

    # Check if already seeded
    if db.query(User).count() > 0:
        return False

    print("Seeding initial categories, users, channels, videos, and comments...")

    # 1. Categories
    cats_data = [
        ("Technology", "technology", "cpu"),
        ("Programming", "programming", "code"),
        ("Music & Audio", "music", "music"),
        ("Nature & Wildlife", "nature", "globe"),
        ("Education", "education", "book-open"),
        ("Gaming", "gaming", "gamepad-2"),
        ("Cooking", "cooking", "utensils"),
    ]
    categories = {}
    for name, slug, icon in cats_data:
        cat = Category(name=name, slug=slug, icon=icon)
        db.add(cat)
        db.flush()
        categories[slug] = cat

    # 2. Users and Channels
    users_data = [
        {
            "username": "alex_rivers",
            "email": "alex@techvoyager.io",
            "full_name": "Alex Rivers",
            "avatar": "/static/uploads/avatars/user1.svg",
            "bio": "Deep tech enthusiast, AI researcher, and future trends broadcaster.",
            "channel_name": "TechVoyager",
            "handle": "techvoyager",
            "channel_desc": "Welcome to TechVoyager! We explore groundbreaking tech, next-generation AI, autonomous systems, and modern hardware.",
            "banner": "/static/uploads/banners/tech_banner.svg",
            "subs": 1420000,
            "verified": True
        },
        {
            "username": "maya_lofi",
            "email": "maya@lofichill.net",
            "full_name": "Maya Lin",
            "avatar": "/static/uploads/avatars/user2.svg",
            "bio": "Curating relaxing soundscapes for studying, coding, and peaceful nights.",
            "channel_name": "Lo-Fi Chill & Ambient",
            "handle": "lofichill",
            "channel_desc": "Chill beats, ambient synthwave, and low-fidelity melodies to keep you focused and calm.",
            "banner": "/static/uploads/banners/music_banner.svg",
            "subs": 854000,
            "verified": True
        },
        {
            "username": "dave_miller",
            "email": "dave@codecraft.dev",
            "full_name": "Dave Miller",
            "avatar": "/static/uploads/avatars/user3.svg",
            "bio": "Senior Systems Architect & Python/MySQL enthusiast. Teaching practical software engineering.",
            "channel_name": "CodeCraft",
            "handle": "codecraft",
            "channel_desc": "Clear, practical, no-fluff coding tutorials covering Python, MySQL, database optimization, and cloud architecture.",
            "banner": "/static/uploads/banners/code_banner.svg",
            "subs": 429000,
            "verified": True
        },
        {
            "username": "sarah_jenkins",
            "email": "sarah@planetearth4k.org",
            "full_name": "Sarah Jenkins",
            "avatar": "/static/uploads/avatars/user4.svg",
            "bio": "Documentary filmmaker and wildlife conservationist traveling the world in 4K/8K.",
            "channel_name": "Planet Earth 4K",
            "handle": "planetearth4k",
            "channel_desc": "High definition wildlife and natural wonders of planet Earth. Preserving biodiversity through visual storytelling.",
            "banner": "/static/uploads/banners/nature_banner.svg",
            "subs": 2180000,
            "verified": True
        },
        {
            "username": "chef_kevin",
            "email": "kevin@culinarystudio.com",
            "full_name": "Chef Kevin Zhang",
            "avatar": "/static/uploads/avatars/user5.svg",
            "bio": "Passionate chef bringing gourmet restaurant secrets into your home kitchen.",
            "channel_name": "Culinary Arts Studio",
            "handle": "culinaryarts",
            "channel_desc": "Authentic recipes, culinary techniques, knife skills, and food science made accessible.",
            "banner": "/static/uploads/banners/default_banner.svg",
            "subs": 312000,
            "verified": False
        }
    ]

    users = {}
    channels = {}

    for u_info in users_data:
        user = User(
            username=u_info["username"],
            email=u_info["email"],
            full_name=u_info["full_name"],
            avatar_url=u_info["avatar"],
            bio=u_info["bio"]
        )
        db.add(user)
        db.flush()
        users[u_info["username"]] = user

        channel = Channel(
            user_id=user.id,
            channel_name=u_info["channel_name"],
            handle=u_info["handle"],
            description=u_info["channel_desc"],
            avatar_url=u_info["avatar"],
            banner_url=u_info["banner"],
            subscriber_count=u_info["subs"],
            verified=u_info["verified"]
        )
        db.add(channel)
        db.flush()
        channels[u_info["username"]] = channel

    # 3. Subscriptions
    subs_pairs = [
        ("alex_rivers", "maya_lofi"),
        ("alex_rivers", "sarah_jenkins"),
        ("maya_lofi", "dave_miller"),
        ("dave_miller", "alex_rivers"),
        ("sarah_jenkins", "alex_rivers"),
        ("chef_kevin", "maya_lofi")
    ]
    for sub_username, target_channel_user in subs_pairs:
        s = Subscription(
            user_id=users[sub_username].id,
            channel_id=channels[target_channel_user].id
        )
        db.add(s)

    # 4. Videos
    videos_data = [
        {
            "channel_user": "sarah_jenkins",
            "category": "nature",
            "title": "4K Ultra HD Nature Exploration: Blooming Flora & Spring Atmosphere",
            "desc": "A breathtaking high-definition macro visual journey through spring gardens and wildflowers.\n\nCaptured with RED Helium 8K and master-graded in Rec.709. Enjoy calming relaxation and crystal-clear natural details.\n\n#Nature #4K #Relaxation #Botany #Wildlife",
            "video_url": "/static/uploads/videos/sample_nature_flower.mp4",
            "thumb": "/static/uploads/thumbnails/thumb_flower.jpg",
            "duration": "0:05",
            "duration_seconds": 5,
            "views": 142850,
            "likes": 14200,
            "dislikes": 32,
            "tags": "nature, flora, 4k, ultra hd, flowers, relaxation",
            "days_ago": 3
        },
        {
            "channel_user": "alex_rivers",
            "category": "technology",
            "title": "Autonomous City Traffic & Real-time Computer Vision Tracking",
            "desc": "How modern smart cities leverage deep neural networks, YOLO object detection, and edge computing to track vehicles, bicycles, and pedestrians in real time without lag.\n\nIn this video we break down the neural architecture, latency benchmarks, and privacy-preserving inference pipelines.\n\n#AI #ComputerVision #SmartCity #Autonomous #Tech",
            "video_url": "/static/uploads/videos/sample_city_stream.mp4",
            "thumb": "/static/uploads/thumbnails/thumb_city.jpg",
            "duration": "0:14",
            "duration_seconds": 14,
            "views": 98400,
            "likes": 8900,
            "dislikes": 19,
            "tags": "ai, computer vision, smart cities, edge computing, robotics",
            "days_ago": 5
        },
        {
            "channel_user": "maya_lofi",
            "category": "music",
            "title": "Lo-Fi Hip Hop Chill Beats to Relax, Code & Study To (24/7 Mix)",
            "desc": "Sink into this relaxing collection of mellow piano loops, warm vinyl crackles, and gentle downtempo drums. Perfect companion for late night coding sessions, reading, or meditation.\n\nTracklist:\n00:00 - Midnight Stroll\n05:12 - Neon Raindrops\n11:45 - Tokyo Rooftops\n22:30 - Coffee & Terminal\n\n#LoFi #Beats #StudyMusic #ChillHop #CodingMusic",
            "video_url": "https://vjs.zencdn.net/v/oceans.mp4",
            "thumb": "/static/uploads/thumbnails/thumb_music.jpg",
            "duration": "42:15",
            "duration_seconds": 2535,
            "views": 384000,
            "likes": 29500,
            "dislikes": 64,
            "tags": "lofi, chill, study beats, coding music, synthwave, ambient",
            "days_ago": 7
        },
        {
            "channel_user": "dave_miller",
            "category": "programming",
            "title": "Building High-Throughput MySQL & Python Web Applications from Scratch",
            "desc": "An in-depth guide on architecting resilient, production-ready web platforms backed by MySQL and Python. We cover schema design, InnoDB indexing, connection pooling, prepared statements, and async APIs.\n\nChapters:\n0:00 Introduction & Architecture\n3:20 MySQL Relational Schema & Indexes\n8:15 Connection Pooling with PyMySQL\n12:40 FastAPI Streaming & Range Requests\n16:10 Performance Benchmarks\n\n#MySQL #Python #Database #FastAPI #Backend",
            "video_url": "https://vjs.zencdn.net/v/oceans.mp4",
            "thumb": "/static/uploads/thumbnails/thumb_code.jpg",
            "duration": "18:40",
            "duration_seconds": 1120,
            "views": 52400,
            "likes": 4800,
            "dislikes": 12,
            "tags": "mysql, python, fastapi, database, indexing, sql, programming",
            "days_ago": 10
        },
        {
            "channel_user": "sarah_jenkins",
            "category": "nature",
            "title": "Diving with Humpback Whales & Pacific Marine Coral Reef Ecosystems",
            "desc": "Journey deep beneath the Pacific ocean as we swim alongside majestic humpback whales and investigate coral reef rehabilitation initiatives.\n\nShot on underwater Arri Alexa Mini with specialized hydrophone audio recordings.\n\n#Ocean #MarineLife #Whales #Documentary #CoralReef",
            "video_url": "https://vjs.zencdn.net/v/oceans.mp4",
            "thumb": "/static/uploads/thumbnails/thumb_nature.jpg",
            "duration": "12:30",
            "duration_seconds": 750,
            "views": 1250400,
            "likes": 98000,
            "dislikes": 140,
            "tags": "ocean, marine, whales, coral reef, documentary, wildlife",
            "days_ago": 14
        },
        {
            "channel_user": "chef_kevin",
            "category": "cooking",
            "title": "The Ultimate Guide to Authentic Japanese Tonkotsu Ramen at Home",
            "desc": "Master the rich, silky broth, perfectly marinated ajitsuke tamago (soft-boiled eggs), tender chashu pork belly, and fresh springy noodles completely from scratch.\n\nStep by step tips on emulsification and tare balance!\n\n#Ramen #Cooking #JapaneseFood #Culinary #Chef",
            "video_url": "/static/uploads/videos/sample_nature_flower.mp4",
            "thumb": "/static/uploads/thumbnails/thumb_cooking.jpg",
            "duration": "22:10",
            "duration_seconds": 1330,
            "views": 76000,
            "likes": 6100,
            "dislikes": 18,
            "tags": "ramen, cooking, food, recipe, japanese, dinner",
            "days_ago": 18
        }
    ]

    videos = []
    now = datetime.datetime.utcnow()
    for vd in videos_data:
        created_time = now - datetime.timedelta(days=vd["days_ago"], hours=4)
        v = Video(
            channel_id=channels[vd["channel_user"]].id,
            title=vd["title"],
            description=vd["desc"],
            video_url=vd["video_url"],
            thumbnail_url=vd["thumb"],
            duration=vd["duration"],
            duration_seconds=vd["duration_seconds"],
            views_count=vd["views"],
            likes_count=vd["likes"],
            dislikes_count=vd["dislikes"],
            category_id=categories[vd["category"]].id,
            tags=vd["tags"],
            visibility="public",
            created_at=created_time
        )
        db.add(v)
        db.flush()
        videos.append(v)

    # 5. Comments
    comments_data = [
        (0, "alex_rivers", "The color grading and clarity here is magnificent! What macro lens did you use for the pollen shot?"),
        (0, "dave_miller", "Super soothing. Put this on loop while testing our database migrations."),
        (1, "dave_miller", "Brilliant breakdown of the latency tradeoff with edge model quantization. Really enjoyed the FPS comparison chart!"),
        (1, "sarah_jenkins", "The pace of computer vision advancements in just the last two years is astonishing."),
        (2, "chef_kevin", "This playlist plays on repeat in our kitchen every single morning prep. Never gets old!"),
        (2, "alex_rivers", "Top tier production value on the audio master. Subscribed!"),
        (3, "alex_rivers", "Essential watching for anyone connecting FastAPI with relational databases. Excellent indexing tips."),
        (3, "maya_lofi", "Finally someone explains InnoDB clustered indexes without overcomplicating it. Thank you Dave!")
    ]

    for v_idx, commenter_username, content in comments_data:
        c = Comment(
            video_id=videos[v_idx].id,
            user_id=users[commenter_username].id,
            content=content,
            likes_count=12,
            created_at=now - datetime.timedelta(days=1, hours=2)
        )
        db.add(c)

    # 6. Sample reactions and Watch History for primary user
    primary_user = users["alex_rivers"]
    db.add(VideoReaction(video_id=videos[0].id, user_id=primary_user.id, reaction_type="like"))
    db.add(VideoReaction(video_id=videos[2].id, user_id=primary_user.id, reaction_type="like"))
    db.add(WatchHistory(user_id=primary_user.id, video_id=videos[0].id, progress_seconds=4))
    db.add(WatchHistory(user_id=primary_user.id, video_id=videos[1].id, progress_seconds=12))

    db.commit()
    print("Seeding completed successfully!")
    return True
