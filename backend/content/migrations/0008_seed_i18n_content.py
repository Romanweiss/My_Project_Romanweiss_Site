from django.db import migrations


BRAND_NAME = "Romanweiẞ"

TRANSLATIONS = {
    "brand.name": {
        "en": BRAND_NAME,
        "ru": BRAND_NAME,
        "zh": BRAND_NAME,
    },
    "status.loading": {
        "en": "Loading content...",
        "ru": "Загрузка контента...",
        "zh": "正在加载内容...",
    },
    "status.unavailable": {
        "en": "Content is unavailable.",
        "ru": "Контент недоступен.",
        "zh": "内容不可用。",
    },
    "lang.en": {"en": "EN", "ru": "EN", "zh": "EN"},
    "lang.ru": {"en": "RU", "ru": "RU", "zh": "RU"},
    "lang.zh": {"en": "中文", "ru": "中文", "zh": "中文"},
    "lang.switcher": {"en": "Language", "ru": "Язык", "zh": "语言"},
    "theme.light": {
        "en": "Light",
        "ru": "Светлая",
        "zh": "浅色",
    },
    "theme.dark": {
        "en": "Dark",
        "ru": "Тёмная",
        "zh": "深色",
    },
    "nav.journey": {
        "en": "Journey",
        "ru": "Путь",
        "zh": "旅程",
    },
    "nav.expeditions": {
        "en": "Expeditions",
        "ru": "Экспедиции",
        "zh": "探险",
    },
    "nav.stories": {
        "en": "Stories",
        "ru": "Истории",
        "zh": "故事",
    },
    "nav.contact": {
        "en": "Contact",
        "ru": "Контакты",
        "zh": "联系",
    },
    "footer.nav.expeditions": {
        "en": "Expeditions",
        "ru": "Экспедиции",
        "zh": "探险",
    },
    "footer.nav.stories": {
        "en": "Journal",
        "ru": "Журнал",
        "zh": "日志",
    },
    "footer.nav.prints": {
        "en": "Prints",
        "ru": "Принты",
        "zh": "作品印刷",
    },
    "footer.nav.collaborate": {
        "en": "Collaborate",
        "ru": "Сотрудничество",
        "zh": "合作",
    },
    "social.ig": {"en": "IG", "ru": "IG", "zh": "IG"},
    "social.x": {"en": "X", "ru": "X", "zh": "X"},
    "social.mail": {"en": "Mail", "ru": "Почта", "zh": "邮箱"},
    "section.hero.title": {
        "en": BRAND_NAME,
        "ru": BRAND_NAME,
        "zh": BRAND_NAME,
    },
    "section.hero.subtitle": {
        "en": "Travel and expedition photography.",
        "ru": "Тревел и экспедиционная фотография.",
        "zh": "旅行与探险摄影。",
    },
    "section.hero.kicker": {
        "en": "Travel and expedition photography",
        "ru": "Тревел и экспедиционная фотография",
        "zh": "旅行与探险摄影",
    },
    "section.hero.scroll_label": {
        "en": "Scroll to begin",
        "ru": "Прокрутите вниз",
        "zh": "向下滚动开始",
    },
    "section.journal_intro.body": {
        "en": "Journal notes from routes and remote places.",
        "ru": "Записи о маршрутах и удалённых местах.",
        "zh": "关于路线与远方地点的日志记录。",
    },
    "section.expeditions.eyebrow": {
        "en": "Journal",
        "ru": "Журнал",
        "zh": "日志",
    },
    "section.expeditions.title": {
        "en": "Recent expeditions",
        "ru": "Последние экспедиции",
        "zh": "最新探险",
    },
    "section.expeditions.subtitle": {
        "en": "Routes through remote locations.",
        "ru": "Маршруты по удалённым локациям.",
        "zh": "通往偏远地点的路线。",
    },
    "section.expeditions.action_label": {
        "en": "View all",
        "ru": "Смотреть всё",
        "zh": "查看全部",
    },
    "section.categories.eyebrow": {
        "en": "Portfolio",
        "ru": "Портфолио",
        "zh": "作品集",
    },
    "section.categories.title": {
        "en": "Focus areas",
        "ru": "Направления",
        "zh": "创作方向",
    },
    "section.categories.subtitle": {
        "en": "Visual grouping through imagery.",
        "ru": "Визуальные группы через изображение.",
        "zh": "通过影像进行视觉分组。",
    },
    "section.stories.eyebrow": {
        "en": "Visual stories",
        "ru": "Визуальные истории",
        "zh": "视觉故事",
    },
    "section.stories.title": {
        "en": "Selected stories",
        "ru": "Избранные истории",
        "zh": "精选故事",
    },
    "section.stories.action_label": {
        "en": "Read full story",
        "ru": "Читать полностью",
        "zh": "阅读完整故事",
    },
    "section.contact.title": {
        "en": "Get in touch",
        "ru": "Связаться",
        "zh": "联系我",
    },
    "section.contact.body": {
        "en": "Open to collaboration and project requests.",
        "ru": "Открыт к сотрудничеству и проектным запросам.",
        "zh": "欢迎合作与项目咨询。",
    },
    "detail.location": {"en": "Location", "ru": "Локация", "zh": "地点"},
    "detail.email": {"en": "Email", "ru": "Почта", "zh": "邮箱"},
    "detail.socials": {"en": "Socials", "ru": "Соцсети", "zh": "社交"},
    "form.name.label": {"en": "Name", "ru": "Имя", "zh": "姓名"},
    "form.name.placeholder": {
        "en": "Your name",
        "ru": "Ваше имя",
        "zh": "你的姓名",
    },
    "form.email.label": {"en": "Email", "ru": "Почта", "zh": "邮箱"},
    "form.email.placeholder": {
        "en": "your@email.com",
        "ru": "your@email.com",
        "zh": "your@email.com",
    },
    "form.message.label": {"en": "Message", "ru": "Сообщение", "zh": "留言"},
    "form.message.placeholder": {
        "en": "Tell me about your project...",
        "ru": "Расскажите о вашем проекте...",
        "zh": "请介绍一下你的项目...",
    },
    "form.submit": {
        "en": "Send message",
        "ru": "Отправить сообщение",
        "zh": "发送消息",
    },
    "form.sending": {"en": "Sending...", "ru": "Отправка...", "zh": "发送中..."},
    "form.success": {
        "en": "Message sent. Thank you.",
        "ru": "Сообщение отправлено. Спасибо.",
        "zh": "消息已发送。谢谢。",
    },
    "form.error": {
        "en": "Could not send message.",
        "ru": "Не удалось отправить сообщение.",
        "zh": "发送失败。",
    },
    "footer.title": {
        "en": BRAND_NAME,
        "ru": BRAND_NAME,
        "zh": BRAND_NAME,
    },
    "footer.description": {
        "en": "Travel stories from remote places.",
        "ru": "Истории путешествий из удалённых мест.",
        "zh": "来自远方地点的旅行故事。",
    },
    "footer.explore": {"en": "Explore", "ru": "Разделы", "zh": "探索"},
    "footer.social": {"en": "Social", "ru": "Соцсети", "zh": "社交"},
    "footer.newsletter": {"en": "Newsletter", "ru": "Рассылка", "zh": "订阅"},
    "footer.newsletter_note": {
        "en": "Monthly route updates.",
        "ru": "Ежемесячные обновления маршрутов.",
        "zh": "每月路线更新。",
    },
    "newsletter.placeholder": {
        "en": "Email address",
        "ru": "Email адрес",
        "zh": "邮箱地址",
    },
    "newsletter.button": {"en": "Join", "ru": "Подписаться", "zh": "订阅"},
}


def _upsert_translation(Translation, language, translation_key, text):
    row = Translation.objects.filter(language=language, key=translation_key).first()
    if row:
        row.text = text
        row.save(update_fields=["text", "updated_at"])
    else:
        Translation.objects.create(language=language, key=translation_key, text=text)


def seed_i18n_content(apps, schema_editor):
    Language = apps.get_model("content", "Language")
    Page = apps.get_model("content", "Page")
    PageSection = apps.get_model("content", "PageSection")
    SiteSettings = apps.get_model("content", "SiteSettings")
    TranslationKey = apps.get_model("content", "TranslationKey")
    Translation = apps.get_model("content", "Translation")

    en, _ = Language.objects.update_or_create(
        code="en",
        defaults={
            "name": "English",
            "is_default": True,
            "is_active": True,
            "order": 1,
        },
    )
    ru, _ = Language.objects.update_or_create(
        code="ru",
        defaults={
            "name": "Русский",
            "is_default": False,
            "is_active": True,
            "order": 2,
        },
    )
    zh, _ = Language.objects.update_or_create(
        code="zh",
        defaults={
            "name": "中文",
            "is_default": False,
            "is_active": True,
            "order": 3,
        },
    )
    Language.objects.exclude(pk=en.pk).filter(is_default=True).update(is_default=False)

    site_settings = SiteSettings.objects.order_by("-updated_at").first()
    if site_settings:
        site_settings.brand_name = BRAND_NAME
        site_settings.footer_title = BRAND_NAME
        brand_map = dict(site_settings.brand_name_i18n or {})
        brand_map.update({"en": BRAND_NAME, "ru": BRAND_NAME, "zh": BRAND_NAME})
        site_settings.brand_name_i18n = brand_map
        footer_title_map = dict(site_settings.footer_title_i18n or {})
        footer_title_map.update({"en": BRAND_NAME, "ru": BRAND_NAME, "zh": BRAND_NAME})
        site_settings.footer_title_i18n = footer_title_map
        site_settings.save(
            update_fields=[
                "brand_name",
                "footer_title",
                "brand_name_i18n",
                "footer_title_i18n",
                "updated_at",
            ]
        )

    slug_defaults = [
        ("home", "Home", 1, True),
        ("journey", "Journey", 2, False),
        ("expeditions", "Expeditions", 3, False),
        ("stories", "Stories", 4, False),
        ("contact", "Contact", 5, False),
    ]
    for slug, title, order, is_home in slug_defaults:
        page, created = Page.objects.get_or_create(
            slug=slug,
            defaults={
                "title": title,
                "is_home": is_home,
                "is_active": True,
                "is_published": True,
                "order": order,
            },
        )
        page.is_active = True
        page.order = order
        if slug == "home":
            page.is_home = True
        page.save(update_fields=["is_active", "order", "is_home", "updated_at"])

    hero_section = PageSection.objects.filter(key="hero").order_by("id").first()
    if hero_section:
        hero_section.title = BRAND_NAME
        title_map = dict(hero_section.title_i18n or {})
        title_map.update({"en": BRAND_NAME, "ru": BRAND_NAME, "zh": BRAND_NAME})
        hero_section.title_i18n = title_map
        hero_section.save(update_fields=["title", "title_i18n", "updated_at"])

    language_by_code = {"en": en, "ru": ru, "zh": zh}
    for key, values in TRANSLATIONS.items():
        namespace = key.split(".", 1)[0] if "." in key else "core"
        translation_key, _ = TranslationKey.objects.update_or_create(
            key=key,
            defaults={
                "namespace": namespace,
                "description": "",
                "is_active": True,
            },
        )
        for language_code, language in language_by_code.items():
            text = values.get(language_code) or values.get("en") or key
            _upsert_translation(Translation, language, translation_key, text)


def noop_reverse(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0007_i18n_core_schema"),
    ]

    operations = [migrations.RunPython(seed_i18n_content, noop_reverse)]
