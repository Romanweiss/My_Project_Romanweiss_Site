from django.db import migrations, models


UI_TRANSLATIONS = {
    "ru": {
        "loading_content": "Загрузка контента...",
        "content_unavailable": "Контент недоступен.",
        "detail_location": "Локация",
        "detail_email": "Email",
        "detail_socials": "Соцсети",
        "contact_name_label": "Имя",
        "contact_name_placeholder": "Ваше имя",
        "contact_email_label": "Email",
        "contact_email_placeholder": "your@email.com",
        "contact_message_label": "Сообщение",
        "contact_message_placeholder": "Расскажите о вашем проекте...",
        "contact_submit": "Отправить",
        "contact_sending": "Отправка...",
        "contact_success": "Сообщение отправлено. Спасибо.",
        "contact_error_default": "Не удалось отправить сообщение.",
        "newsletter_placeholder": "Email адрес",
        "newsletter_button": "Подписаться",
        "theme_light": "Светлая",
        "theme_dark": "Тёмная",
        "lang_en": "EN",
        "lang_ru": "RU",
        "lang_zh": "中文",
    },
    "zh": {
        "loading_content": "正在加载内容...",
        "content_unavailable": "内容不可用。",
        "detail_location": "地点",
        "detail_email": "邮箱",
        "detail_socials": "社交",
        "contact_name_label": "姓名",
        "contact_name_placeholder": "你的姓名",
        "contact_email_label": "邮箱",
        "contact_email_placeholder": "your@email.com",
        "contact_message_label": "留言",
        "contact_message_placeholder": "请介绍一下你的项目...",
        "contact_submit": "发送消息",
        "contact_sending": "发送中...",
        "contact_success": "消息已发送。谢谢。",
        "contact_error_default": "发送失败。",
        "newsletter_placeholder": "邮箱地址",
        "newsletter_button": "订阅",
        "theme_light": "浅色",
        "theme_dark": "深色",
        "lang_en": "EN",
        "lang_ru": "RU",
        "lang_zh": "中文",
    },
}


def _merge_language_values(existing, updates):
    data = dict(existing or {})
    for lang, value in updates.items():
        if not data.get(lang):
            data[lang] = value
    return data


def _merge_nested(existing, lang, updates):
    data = dict(existing or {})
    language_values = dict(data.get(lang) or {})
    for key, value in updates.items():
        if not language_values.get(key):
            language_values[key] = value
    data[lang] = language_values
    return data


def seed_i18n(apps, schema_editor):
    SiteSettings = apps.get_model("content", "SiteSettings")
    Page = apps.get_model("content", "Page")
    PageSection = apps.get_model("content", "PageSection")
    Menu = apps.get_model("content", "Menu")
    MenuItem = apps.get_model("content", "MenuItem")

    for site in SiteSettings.objects.all():
        site.brand_name_i18n = _merge_language_values(
            site.brand_name_i18n, {"ru": site.brand_name, "zh": site.brand_name}
        )
        site.footer_title_i18n = _merge_language_values(
            site.footer_title_i18n, {"ru": site.footer_title, "zh": site.footer_title}
        )
        site.footer_description_i18n = _merge_language_values(
            site.footer_description_i18n,
            {
                "ru": "Снимаем тишину удалённых мест, фактуру ветра и истории, живущие на расстоянии.",
                "zh": "记录遥远之地的寂静、风的纹理，以及在远方诞生的故事。",
            },
        )
        site.footer_explore_title_i18n = _merge_language_values(
            site.footer_explore_title_i18n,
            {"ru": "Разделы", "zh": "探索"},
        )
        site.footer_social_title_i18n = _merge_language_values(
            site.footer_social_title_i18n,
            {"ru": "Соцсети", "zh": "社交"},
        )
        site.footer_newsletter_title_i18n = _merge_language_values(
            site.footer_newsletter_title_i18n,
            {"ru": "Рассылка", "zh": "订阅"},
        )
        site.newsletter_note_i18n = _merge_language_values(
            site.newsletter_note_i18n,
            {
                "ru": "Обновления из путешествий раз в месяц.",
                "zh": "每月一次的旅行更新。",
            },
        )

        ui_map = dict(site.ui_i18n or {})
        ui_map["ru"] = {**UI_TRANSLATIONS["ru"], **dict(ui_map.get("ru") or {})}
        ui_map["zh"] = {**UI_TRANSLATIONS["zh"], **dict(ui_map.get("zh") or {})}
        site.ui_i18n = ui_map
        site.save(
            update_fields=[
                "brand_name_i18n",
                "footer_title_i18n",
                "footer_description_i18n",
                "footer_explore_title_i18n",
                "footer_social_title_i18n",
                "footer_newsletter_title_i18n",
                "newsletter_note_i18n",
                "ui_i18n",
            ]
        )

    for page in Page.objects.all():
        if page.slug == "home":
            page.title_i18n = _merge_language_values(
                page.title_i18n, {"ru": "Главная", "zh": "首页"}
            )
        page.seo_title_i18n = _merge_language_values(
            page.seo_title_i18n, {"ru": page.seo_title, "zh": page.seo_title}
        )
        page.seo_description_i18n = _merge_language_values(
            page.seo_description_i18n,
            {"ru": page.seo_description, "zh": page.seo_description},
        )
        page.save(
            update_fields=[
                "title_i18n",
                "seo_title_i18n",
                "seo_description_i18n",
            ]
        )

    for section in PageSection.objects.select_related("page").all():
        if section.key == "hero":
            section.title_i18n = _merge_language_values(
                section.title_i18n, {"ru": section.title, "zh": section.title}
            )
            section.subtitle_i18n = _merge_language_values(
                section.subtitle_i18n,
                {
                    "ru": "Исследуя пейзажи, архитектуру и тонкую дистанцию между моментами.",
                    "zh": "探索风景、建筑，以及时刻之间微妙的距离。",
                },
            )
            section.payload_i18n = _merge_nested(
                section.payload_i18n,
                "ru",
                {
                    "kicker": "Тревел и экспедиционная фотография",
                    "scroll_label": "Прокрутите вниз",
                },
            )
            section.payload_i18n = _merge_nested(
                section.payload_i18n,
                "zh",
                {"kicker": "旅行与探险摄影", "scroll_label": "向下滚动开始"},
            )

        if section.key == "journal-intro":
            section.body_i18n = _merge_language_values(
                section.body_i18n,
                {
                    "ru": (
                        "Мы путешествуем не для того, чтобы убежать от жизни, "
                        "а чтобы жизнь не прошла мимо нас. Этот журнал - коллекция моментов в пути."
                    ),
                    "zh": (
                        "我们旅行并非逃离生活，而是为了不让生活从身边溜走。"
                        "这本日志记录了旅途中被光线和静默包围的瞬间。"
                    ),
                },
            )

        if section.key == "expeditions":
            section.payload_i18n = _merge_nested(
                section.payload_i18n,
                "ru",
                {
                    "eyebrow": "Журнал",
                    "title": "Последние экспедиции",
                    "subtitle": "Путешествия в удалённые места.",
                    "action_label": "Смотреть всё ->",
                },
            )
            section.payload_i18n = _merge_nested(
                section.payload_i18n,
                "zh",
                {
                    "eyebrow": "日志",
                    "title": "最新探险",
                    "subtitle": "深入偏远之地的旅程。",
                    "action_label": "查看全部 ->",
                },
            )

        if section.key == "categories":
            section.payload_i18n = _merge_nested(
                section.payload_i18n,
                "ru",
                {
                    "eyebrow": "Портфолио",
                    "title": "Направления",
                    "subtitle": "Визуальное разделение через изображение, а не рамки.",
                },
            )
            section.payload_i18n = _merge_nested(
                section.payload_i18n,
                "zh",
                {
                    "eyebrow": "作品集",
                    "title": "创作方向",
                    "subtitle": "用影像而非边框构建视觉层次。",
                },
            )

        if section.key == "stories":
            section.payload_i18n = _merge_nested(
                section.payload_i18n,
                "ru",
                {
                    "eyebrow": "Визуальные истории",
                    "title": "Избранные истории",
                    "action_label": "Читать полностью",
                },
            )
            section.payload_i18n = _merge_nested(
                section.payload_i18n,
                "zh",
                {
                    "eyebrow": "视觉故事",
                    "title": "精选故事",
                    "action_label": "阅读完整故事",
                },
            )

        if section.key == "contact":
            section.title_i18n = _merge_language_values(
                section.title_i18n,
                {"ru": "Свяжитесь со мной", "zh": "联系我"},
            )
            section.body_i18n = _merge_language_values(
                section.body_i18n,
                {
                    "ru": (
                        "Открыт для коллабораций, заказов принтов и новых творческих проектов."
                    ),
                    "zh": "欢迎合作、作品印刷咨询，或任何新的创意项目交流。",
                },
            )
            section.payload_i18n = _merge_nested(
                section.payload_i18n,
                "ru",
                {"location": "Берлин, Германия"},
            )
            section.payload_i18n = _merge_nested(
                section.payload_i18n,
                "zh",
                {"location": "德国 柏林"},
            )

        section.save(
            update_fields=[
                "title_i18n",
                "subtitle_i18n",
                "body_i18n",
                "payload_i18n",
            ]
        )

    for menu in Menu.objects.all():
        if menu.code == "main":
            menu.title_i18n = _merge_language_values(
                menu.title_i18n,
                {"ru": "Основное меню", "zh": "主导航"},
            )
        elif menu.code == "footer":
            menu.title_i18n = _merge_language_values(
                menu.title_i18n,
                {"ru": "Меню футера", "zh": "页脚导航"},
            )
        elif menu.code == "social":
            menu.title_i18n = _merge_language_values(
                menu.title_i18n,
                {"ru": "Соцсети", "zh": "社交链接"},
            )
        else:
            menu.title_i18n = _merge_language_values(
                menu.title_i18n,
                {"ru": menu.title, "zh": menu.title},
            )
        menu.save(update_fields=["title_i18n"])

    label_map = {
        "Journey": {"ru": "Путешествие", "zh": "旅程"},
        "Expeditions": {"ru": "Экспедиции", "zh": "探险"},
        "Stories": {"ru": "Истории", "zh": "故事"},
        "Contact": {"ru": "Контакты", "zh": "联系"},
        "Journal": {"ru": "Журнал", "zh": "日志"},
        "Prints": {"ru": "Принты", "zh": "作品印刷"},
        "Collaborate": {"ru": "Сотрудничество", "zh": "合作"},
        "Mail": {"ru": "Почта", "zh": "邮件"},
    }
    for item in MenuItem.objects.all():
        mapped = label_map.get(item.label)
        if mapped:
            item.label_i18n = _merge_language_values(item.label_i18n, mapped)
        else:
            item.label_i18n = _merge_language_values(
                item.label_i18n, {"ru": item.label, "zh": item.label}
            )
        item.save(update_fields=["label_i18n"])


def noop_reverse(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0004_seed_cms_bootstrap"),
    ]

    operations = [
        migrations.AddField(
            model_name="menu",
            name="title_i18n",
            field=models.JSONField(blank=True, default=dict, verbose_name="Title translations"),
        ),
        migrations.AddField(
            model_name="menuitem",
            name="label_i18n",
            field=models.JSONField(blank=True, default=dict, verbose_name="Label translations"),
        ),
        migrations.AddField(
            model_name="page",
            name="seo_description_i18n",
            field=models.JSONField(
                blank=True, default=dict, verbose_name="SEO description translations"
            ),
        ),
        migrations.AddField(
            model_name="page",
            name="seo_title_i18n",
            field=models.JSONField(blank=True, default=dict, verbose_name="SEO title translations"),
        ),
        migrations.AddField(
            model_name="page",
            name="title_i18n",
            field=models.JSONField(blank=True, default=dict, verbose_name="Title translations"),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="body_i18n",
            field=models.JSONField(blank=True, default=dict, verbose_name="Body translations"),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="payload_i18n",
            field=models.JSONField(blank=True, default=dict, verbose_name="Payload translations"),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="subtitle_i18n",
            field=models.JSONField(blank=True, default=dict, verbose_name="Subtitle translations"),
        ),
        migrations.AddField(
            model_name="pagesection",
            name="title_i18n",
            field=models.JSONField(blank=True, default=dict, verbose_name="Title translations"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="brand_name_i18n",
            field=models.JSONField(
                blank=True, default=dict, verbose_name="Brand name translations"
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="footer_description_i18n",
            field=models.JSONField(
                blank=True, default=dict, verbose_name="Footer description translations"
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="footer_explore_title_i18n",
            field=models.JSONField(
                blank=True, default=dict, verbose_name="Footer explore title translations"
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="footer_newsletter_title_i18n",
            field=models.JSONField(
                blank=True, default=dict, verbose_name="Footer newsletter title translations"
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="footer_social_title_i18n",
            field=models.JSONField(
                blank=True, default=dict, verbose_name="Footer social title translations"
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="footer_title_i18n",
            field=models.JSONField(blank=True, default=dict, verbose_name="Footer title translations"),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="newsletter_note_i18n",
            field=models.JSONField(
                blank=True, default=dict, verbose_name="Newsletter note translations"
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="ui_i18n",
            field=models.JSONField(blank=True, default=dict, verbose_name="UI translations"),
        ),
        migrations.RunPython(seed_i18n, noop_reverse),
    ]
