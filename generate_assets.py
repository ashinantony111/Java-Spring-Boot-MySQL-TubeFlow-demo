import os
from pathlib import Path

base = Path("static/uploads")
(base / "avatars").mkdir(parents=True, exist_ok=True)
(base / "banners").mkdir(parents=True, exist_ok=True)
(base / "thumbnails").mkdir(parents=True, exist_ok=True)

def write_file(p, content):
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)

# Avatars
avatars = {
    "default.svg": ("#FF0000", "TU"),
    "user1.svg": ("#2563EB", "AR"),  # Alex Rivers (TechVoyager)
    "user2.svg": ("#9333EA", "ML"),  # Maya Lin (LoFi Chill)
    "user3.svg": ("#059669", "DM"),  # Dave Miller (CodeCraft)
    "user4.svg": ("#D97706", "SJ"),  # Sarah Jenkins (PlanetEarth 4K)
    "user5.svg": ("#DC2626", "CK")   # Chef Kevin (Culinary Arts)
}

for name, (color, initials) in avatars.items():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="100" height="100">
  <defs>
    <linearGradient id="grad_{initials}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color}" />
      <stop offset="100%" stop-color="#111827" />
    </linearGradient>
  </defs>
  <circle cx="50" cy="50" r="50" fill="url(#grad_{initials})" />
  <text x="50" y="58" font-family="Segoe UI, -apple-system, Roboto, sans-serif" font-size="36" font-weight="bold" fill="#FFFFFF" text-anchor="middle">{initials}</text>
</svg>"""
    write_file(base / "avatars" / name, svg)

# Banners
banners = {
    "default_banner.svg": ("#1e293b", "#0f172a", "TubeFlow Creator Studio"),
    "tech_banner.svg": ("#1e3a8a", "#0284c7", "TechVoyager - The Future of Technology"),
    "music_banner.svg": ("#581c87", "#d946ef", "Lo-Fi Chill and Ambient Beats 24/7"),
    "nature_banner.svg": ("#064e3b", "#10b981", "Planet Earth 4K - Wildlife and Wonders"),
    "code_banner.svg": ("#111827", "#3b82f6", "CodeCraft - Software Engineering Demystified")
}

for name, (c1, c2, title) in banners.items():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 240" width="1200" height="240">
  <defs>
    <linearGradient id="bg_{name.replace('.svg','')}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}" />
      <stop offset="100%" stop-color="{c2}" />
    </linearGradient>
    <pattern id="grid_{name.replace('.svg','')}" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="1200" height="240" fill="url(#bg_{name.replace('.svg','')})" />
  <rect width="1200" height="240" fill="url(#grid_{name.replace('.svg','')})" />
  <circle cx="1100" cy="60" r="120" fill="rgba(255,255,255,0.03)" />
  <text x="60" y="135" font-family="Segoe UI, -apple-system, Roboto, sans-serif" font-size="42" font-weight="800" fill="#ffffff" letter-spacing="1">{title}</text>
</svg>"""
    write_file(base / "banners" / name, svg)

# Thumbnails
thumbs = {
    "thumb_flower.svg": ("#059669", "#10b981", "SPRING BLOOM", "4K Ultra HD Nature Relaxation", "0:05"),
    "thumb_city.svg": ("#2563EB", "#38bdf8", "AI URBAN SCAN", "Smart City and Autonomous Traffic", "0:14"),
    "thumb_music.svg": ("#7c3aed", "#ec4899", "LO-FI STUDY BEATS", "Relaxing Synthwave Chill Session", "42:15"),
    "thumb_code.svg": ("#0f172a", "#2563eb", "BUILD SCALABLE MYSQL APPS", "Full-Stack Performance Guide 2026", "18:40"),
    "thumb_nature.svg": ("#047857", "#065f46", "PACIFIC OCEAN REEF", "Diving The Deep Blue Wonders", "12:30"),
    "thumb_cooking.svg": ("#b45309", "#f59e0b", "MASTER HOMEMADE RAMEN", "From Scratch in 45 Minutes", "22:10")
}

for name, (c1, c2, badge, title, dur) in thumbs.items():
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" width="640" height="360">
  <defs>
    <linearGradient id="grad_{name.replace('.svg','')}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{c1}" />
      <stop offset="100%" stop-color="{c2}" />
    </linearGradient>
    <pattern id="grid_t_{name.replace('.svg','')}" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>
    </pattern>
  </defs>
  <rect width="640" height="360" fill="url(#grad_{name.replace('.svg','')})" />
  <rect width="640" height="360" fill="url(#grid_t_{name.replace('.svg','')})" />
  <circle cx="520" cy="90" r="100" fill="rgba(255,255,255,0.06)" />
  
  <!-- Play watermark icon -->
  <g transform="translate(280, 140)">
    <circle cx="40" cy="40" r="36" fill="rgba(0,0,0,0.4)" />
    <polygon points="32,25 56,40 32,55" fill="#ffffff" />
  </g>

  <!-- Tag Pill -->
  <rect x="35" y="35" width="{len(badge)*12 + 24}" height="28" rx="6" fill="#FF0000" />
  <text x="45" y="54" font-family="Segoe UI, Roboto, sans-serif" font-size="13" font-weight="bold" fill="#ffffff">{badge}</text>

  <!-- Title -->
  <text x="35" y="315" font-family="Segoe UI, Roboto, sans-serif" font-size="24" font-weight="800" fill="#ffffff">{title}</text>
</svg>"""
    write_file(base / "thumbnails" / name, svg)

print("Generated all avatars, banners, and thumbnails successfully!")
