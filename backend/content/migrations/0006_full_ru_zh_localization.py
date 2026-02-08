from django.db import migrations


BRAND_NAME = "Romanweiẞ"

RU_UI_TEXTS = {
    "loading_content": "Загрузка контента...",
    "content_unavailable": "Контент недоступен.",
    "detail_location": "Место",
    "detail_email": "Почта",
    "detail_socials": "Соцсети",
    "contact_name_label": "Имя",
    "contact_name_placeholder": "Ваше имя",
    "contact_email_label": "Почта",
    "contact_email_placeholder": "your@email.com",
    "contact_message_label": "Сообщение",
    "contact_message_placeholder": "Расскажите о вашем проекте...",
    "contact_submit": "Отправить сообщение",
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
}

ZH_UI_TEXTS = {
    "loading_content": "正在加载内容...",
    "content_unavailable": "内容不可用。",
    "detail_location": "地点",
    "detail_email": "邮箱",
    "detail_socials": "社交媒体",
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
}

EXPEDITION_TITLE_MAP = {
    "Glacial Highlands": {"ru": "Ледниковые нагорья", "zh": "冰川高地"},
    "Desert Passage": {"ru": "Пустынный маршрут", "zh": "沙漠穿行"},
    "City at Dawn": {"ru": "Город на рассвете", "zh": "黎明之城"},
}

EXPEDITION_DATE_MAP = {
    "October 2023": {"ru": "Октябрь 2023", "zh": "2023年10月"},
    "August 2023": {"ru": "Август 2023", "zh": "2023年8月"},
    "May 2023": {"ru": "Май 2023", "zh": "2023年5月"},
}

EXPEDITION_DESCRIPTION_MAP = {
    "Wind-cut ridgelines and slate-blue valleys above the tree line.": {
        "ru": "Хребты, иссечённые ветром, и сланцево-синие долины над линией леса.",
        "zh": "树线之上，风刻山脊，板岩蓝色山谷层层展开。",
    },
    "Long asphalt ribbons leading into rust and sandstone labyrinths.": {
        "ru": "Длинные ленты асфальта уводят к лабиринтам ржавых скал и песчаника.",
        "zh": "漫长公路延伸至锈色与砂岩交织的迷宫。",
    },
    "Neon traces softening into morning fog across concrete canyons.": {
        "ru": "Неоновые следы тают в утреннем тумане среди бетонных каньонов.",
        "zh": "霓虹痕迹在清晨薄雾中柔化，穿过城市峡谷。",
    },
}

CATEGORY_TITLE_MAP = {
    "Landscapes": {"ru": "Пейзажи", "zh": "风景"},
    "Architecture": {"ru": "Архитектура", "zh": "建筑"},
    "Nature": {"ru": "Природа", "zh": "自然"},
    "Travel Series": {"ru": "Путевые серии", "zh": "旅行系列"},
}

STORY_TITLE_MAP = {
    "Echoes of the Mountain": {"ru": "Эхо гор", "zh": "山之回响"},
    "Lost in the Fog": {"ru": "Потерянные в тумане", "zh": "雾中迷途"},
}

STORY_DESCRIPTION_MAP = {
    "Why we climb when the world tells us to stay low.": {
        "ru": "Почему мы идём вверх, когда мир предлагает остаться внизу.",
        "zh": "当世界劝我们低头时，我们为何仍选择攀登。",
    },
    "A morning walk that turned into a journey inward.": {
        "ru": "Утренняя прогулка, которая превратилась в путешествие внутрь себя.",
        "zh": "一次清晨散步，最终成了向内的旅程。",
    },
}

MENU_LABEL_MAP = {
    "Journey": {"ru": "Путь", "zh": "旅程"},
    "Expeditions": {"ru": "Экспедиции", "zh": "探险"},
    "Stories": {"ru": "Истории", "zh": "故事"},
    "Contact": {"ru": "Контакты", "zh": "联系"},
    "Journal": {"ru": "Журнал", "zh": "日志"},
    "Prints": {"ru": "Принты", "zh": "作品印刷"},
    "Collaborate": {"ru": "Сотрудничество", "zh": "合作"},
    "Mail": {"ru": "Почта", "zh": "邮箱"},
    "IG": {"ru": "IG", "zh": "IG"},
    "X": {"ru": "X", "zh": "X"},
}


def _set_lang_text(existing, lang, value):
    data = dict(existing) if isinstance(existing, dict) else {}
    data[lang] = value
    return data


def _set_lang_payload(existing, lang, updates):
    data = dict(existing) if isinstance(existing, dict) else {}
    current = data.get(lang)
    language_values = dict(current) if isinstance(current, dict) else {}
    language_values.update(updates)
    data[lang] = language_values
    return data


def _translate_value(value, translation_map, lang):
    if not isinstance(value, str):
        return value
    mapped = translation_map.get(value)
    if isinstance(mapped, dict):
        return mapped.get(lang, value)
    return value


def _translate_expedition_cards(cards, lang):
    translated = []
    for card in cards if isinstance(cards, list) else []:
        if not isinstance(card, dict):
            translated.append(card)
            continue
        item = dict(card)
        item["title"] = _translate_value(item.get("title"), EXPEDITION_TITLE_MAP, lang)
        item["date_label"] = _translate_value(item.get("date_label"), EXPEDITION_DATE_MAP, lang)
        item["description"] = _translate_value(
            item.get("description"), EXPEDITION_DESCRIPTION_MAP, lang
        )
        translated.append(item)
    return translated


def _translate_category_items(items, lang):
    translated = []
    for category in items if isinstance(items, list) else []:
        if not isinstance(category, dict):
            translated.append(category)
            continue
        item = dict(category)
        item["title"] = _translate_value(item.get("title"), CATEGORY_TITLE_MAP, lang)
        translated.append(item)
    return translated


def _translate_story_items(items, lang):
    translated = []
    for story in items if isinstance(items, list) else []:
        if not isinstance(story, dict):
            translated.append(story)
            continue
        item = dict(story)
        item["title"] = _translate_value(item.get("title"), STORY_TITLE_MAP, lang)
        item["description"] = _translate_value(item.get("description"), STORY_DESCRIPTION_MAP, lang)
        translated.append(item)
    return translated


def apply_full_localization(apps, schema_editor):
    SiteSettings = apps.get_model("content", "SiteSettings")
    Page = apps.get_model("content", "Page")
    PageSection = apps.get_model("content", "PageSection")
    Menu = apps.get_model("content", "Menu")
    MenuItem = apps.get_model("content", "MenuItem")

    for site in SiteSettings.objects.all():
        site.brand_name = BRAND_NAME
        site.footer_title = BRAND_NAME
        site.brand_name_i18n = _set_lang_text(site.brand_name_i18n, "ru", BRAND_NAME)
        site.brand_name_i18n = _set_lang_text(site.brand_name_i18n, "zh", BRAND_NAME)
        site.footer_title_i18n = _set_lang_text(site.footer_title_i18n, "ru", BRAND_NAME)
        site.footer_title_i18n = _set_lang_text(site.footer_title_i18n, "zh", BRAND_NAME)
        site.footer_description_i18n = _set_lang_text(
            site.footer_description_i18n,
            "ru",
            "Снимаем тишину удалённых мест, фактуру ветра и истории, живущие на расстоянии.",
        )
        site.footer_description_i18n = _set_lang_text(
            site.footer_description_i18n,
            "zh",
            "记录遥远之地的寂静、风的纹理，以及在远方诞生的故事。",
        )
        site.footer_explore_title_i18n = _set_lang_text(
            site.footer_explore_title_i18n,
            "ru",
            "Разделы",
        )
        site.footer_explore_title_i18n = _set_lang_text(
            site.footer_explore_title_i18n,
            "zh",
            "探索",
        )
        site.footer_social_title_i18n = _set_lang_text(
            site.footer_social_title_i18n,
            "ru",
            "Соцсети",
        )
        site.footer_social_title_i18n = _set_lang_text(
            site.footer_social_title_i18n,
            "zh",
            "社交媒体",
        )
        site.footer_newsletter_title_i18n = _set_lang_text(
            site.footer_newsletter_title_i18n,
            "ru",
            "Рассылка",
        )
        site.footer_newsletter_title_i18n = _set_lang_text(
            site.footer_newsletter_title_i18n,
            "zh",
            "订阅",
        )
        site.newsletter_note_i18n = _set_lang_text(
            site.newsletter_note_i18n,
            "ru",
            "Обновления из экспедиций раз в месяц.",
        )
        site.newsletter_note_i18n = _set_lang_text(
            site.newsletter_note_i18n,
            "zh",
            "每月一次的探险更新。",
        )

        ui_map = dict(site.ui_i18n or {})
        ru_ui = dict(ui_map.get("ru") or {})
        zh_ui = dict(ui_map.get("zh") or {})
        ru_ui.update(RU_UI_TEXTS)
        zh_ui.update(ZH_UI_TEXTS)
        ui_map["ru"] = ru_ui
        ui_map["zh"] = zh_ui
        site.ui_i18n = ui_map

        site.save(
            update_fields=[
                "brand_name",
                "footer_title",
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
            page.title_i18n = _set_lang_text(page.title_i18n, "ru", "Главная")
            page.title_i18n = _set_lang_text(page.title_i18n, "zh", "首页")
        page.seo_title_i18n = _set_lang_text(page.seo_title_i18n, "ru", BRAND_NAME)
        page.seo_title_i18n = _set_lang_text(page.seo_title_i18n, "zh", BRAND_NAME)
        page.seo_description_i18n = _set_lang_text(
            page.seo_description_i18n,
            "ru",
            "Авторская travel- и экспедиционная фотография с акцентом на атмосферу и дистанцию.",
        )
        page.seo_description_i18n = _set_lang_text(
            page.seo_description_i18n,
            "zh",
            "以氛围与距离感为核心的旅行与探险摄影。",
        )
        page.save(update_fields=["title_i18n", "seo_title_i18n", "seo_description_i18n"])

    for section in PageSection.objects.select_related("page").all():
        if section.key == "hero":
            section.title = BRAND_NAME
            section.title_i18n = _set_lang_text(section.title_i18n, "ru", BRAND_NAME)
            section.title_i18n = _set_lang_text(section.title_i18n, "zh", BRAND_NAME)
            section.subtitle_i18n = _set_lang_text(
                section.subtitle_i18n,
                "ru",
                "Исследуя пейзажи, архитектуру и тонкую дистанцию между моментами.",
            )
            section.subtitle_i18n = _set_lang_text(
                section.subtitle_i18n,
                "zh",
                "探索风景、建筑，以及时刻之间微妙的距离。",
            )
            section.payload_i18n = _set_lang_payload(
                section.payload_i18n,
                "ru",
                {
                    "kicker": "Тревел- и экспедиционная фотография",
                    "scroll_label": "Прокрутите вниз",
                },
            )
            section.payload_i18n = _set_lang_payload(
                section.payload_i18n,
                "zh",
                {
                    "kicker": "旅行与探险摄影",
                    "scroll_label": "向下滚动开始",
                },
            )

        if section.key == "journal-intro":
            section.body_i18n = _set_lang_text(
                section.body_i18n,
                "ru",
                (
                    "Мы путешествуем не для того, чтобы убежать от жизни, "
                    "а чтобы жизнь не прошла мимо нас. Этот журнал - коллекция моментов в пути."
                ),
            )
            section.body_i18n = _set_lang_text(
                section.body_i18n,
                "zh",
                (
                    "我们旅行并非逃离生活，而是为了不让生活从身边溜走。"
                    "这本日志记录了旅途中被光线和静默包围的瞬间。"
                ),
            )

        if section.key == "expeditions":
            cards = []
            if isinstance(section.payload, dict):
                cards = section.payload.get("cards") or []
            section.payload_i18n = _set_lang_payload(
                section.payload_i18n,
                "ru",
                {
                    "eyebrow": "Журнал",
                    "title": "Последние экспедиции",
                    "subtitle": "Путешествия в удалённые места.",
                    "action_label": "Смотреть всё ->",
                    "cards": _translate_expedition_cards(cards, "ru"),
                },
            )
            section.payload_i18n = _set_lang_payload(
                section.payload_i18n,
                "zh",
                {
                    "eyebrow": "日志",
                    "title": "最新探险",
                    "subtitle": "深入偏远之地的旅程。",
                    "action_label": "查看全部 ->",
                    "cards": _translate_expedition_cards(cards, "zh"),
                },
            )

        if section.key == "categories":
            items = []
            if isinstance(section.payload, dict):
                items = section.payload.get("items") or []
            section.payload_i18n = _set_lang_payload(
                section.payload_i18n,
                "ru",
                {
                    "eyebrow": "Портфолио",
                    "title": "Направления",
                    "subtitle": "Визуальное разделение через изображение, а не рамки.",
                    "items": _translate_category_items(items, "ru"),
                },
            )
            section.payload_i18n = _set_lang_payload(
                section.payload_i18n,
                "zh",
                {
                    "eyebrow": "作品集",
                    "title": "创作方向",
                    "subtitle": "用影像而非边框构建视觉层次。",
                    "items": _translate_category_items(items, "zh"),
                },
            )

        if section.key == "stories":
            items = []
            if isinstance(section.payload, dict):
                items = section.payload.get("items") or []
            section.payload_i18n = _set_lang_payload(
                section.payload_i18n,
                "ru",
                {
                    "eyebrow": "Визуальные истории",
                    "title": "Избранные истории",
                    "action_label": "Читать полностью",
                    "items": _translate_story_items(items, "ru"),
                },
            )
            section.payload_i18n = _set_lang_payload(
                section.payload_i18n,
                "zh",
                {
                    "eyebrow": "视觉故事",
                    "title": "精选故事",
                    "action_label": "阅读完整故事",
                    "items": _translate_story_items(items, "zh"),
                },
            )

        if section.key == "contact":
            section.title_i18n = _set_lang_text(section.title_i18n, "ru", "Связаться")
            section.title_i18n = _set_lang_text(section.title_i18n, "zh", "联系我")
            section.body_i18n = _set_lang_text(
                section.body_i18n,
                "ru",
                "Открыт для коллабораций, заказов принтов и новых творческих проектов.",
            )
            section.body_i18n = _set_lang_text(
                section.body_i18n,
                "zh",
                "欢迎合作、作品印刷咨询，或任何新的创意项目交流。",
            )
            section.payload_i18n = _set_lang_payload(
                section.payload_i18n,
                "ru",
                {"location": "Берлин, Германия"},
            )
            section.payload_i18n = _set_lang_payload(
                section.payload_i18n,
                "zh",
                {"location": "德国 柏林"},
            )

        section.save(
            update_fields=[
                "title",
                "title_i18n",
                "subtitle_i18n",
                "body_i18n",
                "payload_i18n",
            ]
        )

    for menu in Menu.objects.all():
        if menu.code == "main":
            menu.title_i18n = _set_lang_text(menu.title_i18n, "ru", "Основная навигация")
            menu.title_i18n = _set_lang_text(menu.title_i18n, "zh", "主导航")
        elif menu.code == "footer":
            menu.title_i18n = _set_lang_text(menu.title_i18n, "ru", "Навигация футера")
            menu.title_i18n = _set_lang_text(menu.title_i18n, "zh", "页脚导航")
        elif menu.code == "social":
            menu.title_i18n = _set_lang_text(menu.title_i18n, "ru", "Соцсети")
            menu.title_i18n = _set_lang_text(menu.title_i18n, "zh", "社交链接")
        menu.save(update_fields=["title_i18n"])

    for item in MenuItem.objects.all():
        mapped = MENU_LABEL_MAP.get(item.label)
        if isinstance(mapped, dict):
            item.label_i18n = _set_lang_text(item.label_i18n, "ru", mapped["ru"])
            item.label_i18n = _set_lang_text(item.label_i18n, "zh", mapped["zh"])
        else:
            item.label_i18n = _set_lang_text(item.label_i18n, "ru", item.label)
            item.label_i18n = _set_lang_text(item.label_i18n, "zh", item.label)
        item.save(update_fields=["label_i18n"])


def noop_reverse(apps, schema_editor):
    return None


class Migration(migrations.Migration):
    dependencies = [
        ("content", "0005_i18n_fields"),
    ]

    operations = [migrations.RunPython(apply_full_localization, noop_reverse)]
