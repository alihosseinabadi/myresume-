"""Section headings in 24 locales — powers the "multilingual templates" feature.

Heading keys are the canonical English labels used across the app. Unknown keys
or missing locales fall back to the English heading so translation can never
break a document.
"""

from __future__ import annotations

HEADING_KEYS: list[str] = [
    "Summary", "Experience", "Education", "Skills", "Languages", "Projects",
    "Certifications", "Awards", "Interests", "Volunteering", "Publications",
    "Courses", "References", "Additional information", "Contact", "Achievements",
]

LOCALE_NAMES: dict[str, str] = {
    "en": "English", "fr": "French", "de": "German", "es": "Spanish",
    "it": "Italian", "pt": "Portuguese", "nl": "Dutch", "sv": "Swedish",
    "no": "Norwegian", "da": "Danish", "fi": "Finnish", "pl": "Polish",
    "cs": "Czech", "ro": "Romanian", "el": "Greek", "ru": "Russian",
    "uk": "Ukrainian", "tr": "Turkish", "ar": "Arabic", "fa": "Persian",
    "he": "Hebrew", "hi": "Hindi", "zh": "Chinese", "ja": "Japanese",
    "ko": "Korean",
}

HEADING_TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {k: k for k in HEADING_KEYS},
    "fr": {
        "Summary": "Profil", "Experience": "Expérience professionnelle",
        "Education": "Formation", "Skills": "Compétences", "Languages": "Langues",
        "Projects": "Projets", "Certifications": "Certifications",
        "Awards": "Distinctions", "Interests": "Centres d'intérêt",
        "Volunteering": "Bénévolat", "Publications": "Publications",
        "Courses": "Formations", "References": "Références",
        "Additional information": "Informations complémentaires",
        "Contact": "Contact", "Achievements": "Réalisations",
    },
    "de": {
        "Summary": "Profil", "Experience": "Berufserfahrung",
        "Education": "Ausbildung", "Skills": "Kenntnisse", "Languages": "Sprachen",
        "Projects": "Projekte", "Certifications": "Zertifikate",
        "Awards": "Auszeichnungen", "Interests": "Interessen",
        "Volunteering": "Ehrenamt", "Publications": "Publikationen",
        "Courses": "Weiterbildungen", "References": "Referenzen",
        "Additional information": "Zusätzliche Informationen",
        "Contact": "Kontakt", "Achievements": "Erfolge",
    },
    "es": {
        "Summary": "Perfil", "Experience": "Experiencia profesional",
        "Education": "Formación", "Skills": "Competencias", "Languages": "Idiomas",
        "Projects": "Proyectos", "Certifications": "Certificaciones",
        "Awards": "Premios", "Interests": "Intereses", "Volunteering": "Voluntariado",
        "Publications": "Publicaciones", "Courses": "Cursos",
        "References": "Referencias",
        "Additional information": "Información adicional",
        "Contact": "Contacto", "Achievements": "Logros",
    },
    "it": {
        "Summary": "Profilo", "Experience": "Esperienza professionale",
        "Education": "Formazione", "Skills": "Competenze", "Languages": "Lingue",
        "Projects": "Progetti", "Certifications": "Certificazioni",
        "Awards": "Premi", "Interests": "Interessi", "Volunteering": "Volontariato",
        "Publications": "Pubblicazioni", "Courses": "Corsi",
        "References": "Referenze",
        "Additional information": "Informazioni aggiuntive",
        "Contact": "Contatti", "Achievements": "Risultati",
    },
    "pt": {
        "Summary": "Perfil", "Experience": "Experiência profissional",
        "Education": "Formação académica", "Skills": "Competências",
        "Languages": "Idiomas", "Projects": "Projetos",
        "Certifications": "Certificações", "Awards": "Prémios",
        "Interests": "Interesses", "Volunteering": "Voluntariado",
        "Publications": "Publicações", "Courses": "Cursos",
        "References": "Referências", "Additional information": "Informação adicional",
        "Contact": "Contacto", "Achievements": "Conquistas",
    },
    "nl": {
        "Summary": "Profiel", "Experience": "Werkervaring",
        "Education": "Opleiding", "Skills": "Vaardigheden", "Languages": "Talen",
        "Projects": "Projecten", "Certifications": "Certificaten",
        "Awards": "Onderscheidingen", "Interests": "Interesses",
        "Volunteering": "Vrijwilligerswerk", "Publications": "Publicaties",
        "Courses": "Cursussen", "References": "Referenties",
        "Additional information": "Aanvullende informatie",
        "Contact": "Contact", "Achievements": "Prestaties",
    },
    "sv": {
        "Summary": "Profil", "Experience": "Arbetslivserfarenhet",
        "Education": "Utbildning", "Skills": "Kompetenser", "Languages": "Språk",
        "Projects": "Projekt", "Certifications": "Certifieringar",
        "Awards": "Priser", "Interests": "Intressen",
        "Volunteering": "Ideellt arbete", "Publications": "Publikationer",
        "Courses": "Kurser", "References": "Referenser",
        "Additional information": "Övrig information",
        "Contact": "Kontakt", "Achievements": "Resultat",
    },
    "no": {
        "Summary": "Profil", "Experience": "Arbeidserfaring",
        "Education": "Utdanning", "Skills": "Ferdigheter", "Languages": "Språk",
        "Projects": "Prosjekter", "Certifications": "Sertifiseringer",
        "Awards": "Priser", "Interests": "Interesser",
        "Volunteering": "Frivillig arbeid", "Publications": "Publikasjoner",
        "Courses": "Kurs", "References": "Referanser",
        "Additional information": "Tilleggsinformasjon",
        "Contact": "Kontakt", "Achievements": "Resultater",
    },
    "da": {
        "Summary": "Profil", "Experience": "Erhvervserfaring",
        "Education": "Uddannelse", "Skills": "Kompetencer", "Languages": "Sprog",
        "Projects": "Projekter", "Certifications": "Certificeringer",
        "Awards": "Priser", "Interests": "Interesser",
        "Volunteering": "Frivilligt arbejde", "Publications": "Publikationer",
        "Courses": "Kurser", "References": "Referencer",
        "Additional information": "Yderligere oplysninger",
        "Contact": "Kontakt", "Achievements": "Resultater",
    },
    "fi": {
        "Summary": "Profiili", "Experience": "Työkokemus",
        "Education": "Koulutus", "Skills": "Taidot", "Languages": "Kielet",
        "Projects": "Projektit", "Certifications": "Sertifikaatit",
        "Awards": "Palkinnot", "Interests": "Kiinnostuksen kohteet",
        "Volunteering": "Vapaaehtoistyö", "Publications": "Julkaisut",
        "Courses": "Kurssit", "References": "Suositukset",
        "Additional information": "Lisätiedot",
        "Contact": "Yhteystiedot", "Achievements": "Saavutukset",
    },
    "pl": {
        "Summary": "Profil", "Experience": "Doświadczenie zawodowe",
        "Education": "Wykształcenie", "Skills": "Umiejętności",
        "Languages": "Języki", "Projects": "Projekty",
        "Certifications": "Certyfikaty", "Awards": "Nagrody",
        "Interests": "Zainteresowania", "Volunteering": "Wolontariat",
        "Publications": "Publikacje", "Courses": "Kursy",
        "References": "Referencje", "Additional information": "Informacje dodatkowe",
        "Contact": "Kontakt", "Achievements": "Osiągnięcia",
    },
    "cs": {
        "Summary": "Profil", "Experience": "Pracovní zkušenosti",
        "Education": "Vzdělání", "Skills": "Dovednosti", "Languages": "Jazyky",
        "Projects": "Projekty", "Certifications": "Certifikace",
        "Awards": "Ocenění", "Interests": "Zájmy", "Volunteering": "Dobrovolnictví",
        "Publications": "Publikace", "Courses": "Kurzy",
        "References": "Reference", "Additional information": "Doplňující informace",
        "Contact": "Kontakt", "Achievements": "Úspěchy",
    },
    "ro": {
        "Summary": "Profil", "Experience": "Experiență profesională",
        "Education": "Educație", "Skills": "Competențe", "Languages": "Limbi străine",
        "Projects": "Proiecte", "Certifications": "Certificări",
        "Awards": "Premii", "Interests": "Interese", "Volunteering": "Voluntariat",
        "Publications": "Publicații", "Courses": "Cursuri",
        "References": "Referințe", "Additional information": "Informații suplimentare",
        "Contact": "Contact", "Achievements": "Realizări",
    },
    "el": {
        "Summary": "Προφίλ", "Experience": "Επαγγελματική εμπειρία",
        "Education": "Εκπαίδευση", "Skills": "Δεξιότητες", "Languages": "Γλώσσες",
        "Projects": "Έργα", "Certifications": "Πιστοποιήσεις",
        "Awards": "Βραβεία", "Interests": "Ενδιαφέροντα",
        "Volunteering": "Εθελοντισμός", "Publications": "Δημοσιεύσεις",
        "Courses": "Σεμινάρια", "References": "Συστάσεις",
        "Additional information": "Πρόσθετες πληροφορίες",
        "Contact": "Επικοινωνία", "Achievements": "Επιτεύγματα",
    },
    "ru": {
        "Summary": "О себе", "Experience": "Опыт работы", "Education": "Образование",
        "Skills": "Навыки", "Languages": "Языки", "Projects": "Проекты",
        "Certifications": "Сертификаты", "Awards": "Награды",
        "Interests": "Интересы", "Volunteering": "Волонтёрство",
        "Publications": "Публикации", "Courses": "Курсы",
        "References": "Рекомендации",
        "Additional information": "Дополнительная информация",
        "Contact": "Контакты", "Achievements": "Достижения",
    },
    "uk": {
        "Summary": "Про себе", "Experience": "Досвід роботи", "Education": "Освіта",
        "Skills": "Навички", "Languages": "Мови", "Projects": "Проєкти",
        "Certifications": "Сертифікати", "Awards": "Нагороди",
        "Interests": "Інтереси", "Volunteering": "Волонтерство",
        "Publications": "Публікації", "Courses": "Курси",
        "References": "Рекомендації",
        "Additional information": "Додаткова інформація",
        "Contact": "Контакти", "Achievements": "Досягнення",
    },
    "tr": {
        "Summary": "Profil", "Experience": "İş deneyimi", "Education": "Eğitim",
        "Skills": "Yetenekler", "Languages": "Diller", "Projects": "Projeler",
        "Certifications": "Sertifikalar", "Awards": "Ödüller",
        "Interests": "İlgi alanları", "Volunteering": "Gönüllülük",
        "Publications": "Yayınlar", "Courses": "Kurslar",
        "References": "Referanslar", "Additional information": "Ek bilgiler",
        "Contact": "İletişim", "Achievements": "Başarılar",
    },
    "ar": {
        "Summary": "الملف الشخصي", "Experience": "الخبرة المهنية",
        "Education": "التعليم", "Skills": "المهارات", "Languages": "اللغات",
        "Projects": "المشاريع", "Certifications": "الشهادات", "Awards": "الجوائز",
        "Interests": "الاهتمامات", "Volunteering": "العمل التطوعي",
        "Publications": "المنشورات", "Courses": "الدورات",
        "References": "المراجع",
        "Additional information": "معلومات إضافية",
        "Contact": "معلومات الاتصال", "Achievements": "الإنجازات",
    },
    "fa": {
        "Summary": "خلاصهٔ حرفهای", "Experience": "سابقهٔ کاری",
        "Education": "تحصیلات", "Skills": "مهارتها", "Languages": "زبانها",
        "Projects": "پروژهها", "Certifications": "گواهینامهها",
        "Awards": "افتخارات", "Interests": "علاقهمندیها",
        "Volunteering": "کار داوطلبانه", "Publications": "انتشارات",
        "Courses": "دورههای آموزشی", "References": "معرفها",
        "Additional information": "اطلاعات تکمیلی",
        "Contact": "اطلاعات تماس", "Achievements": "دستاوردها",
    },
    "he": {
        "Summary": "פרופיל", "Experience": "ניסיון מקצועי", "Education": "השכלה",
        "Skills": "כישורים", "Languages": "שפות", "Projects": "פרויקטים",
        "Certifications": "הסמכות", "Awards": "פרסים", "Interests": "תחומי עניין",
        "Volunteering": "התנדבות", "Publications": "פרסומים", "Courses": "קורסים",
        "References": "המלצות", "Additional information": "מידע נוסף",
        "Contact": "יצירת קשר", "Achievements": "הישגים",
    },
    "hi": {
        "Summary": "प्रोफ़ाइल", "Experience": "कार्य अनुभव", "Education": "शिक्षा",
        "Skills": "कौशल", "Languages": "भाषाएँ", "Projects": "परियोजनाएँ",
        "Certifications": "प्रमाणपत्र", "Awards": "पुरस्कार", "Interests": "रुचियाँ",
        "Volunteering": "स्वयंसेवा", "Publications": "प्रकाशन", "Courses": "पाठ्यक्रम",
        "References": "संदर्भ", "Additional information": "अतिरिक्त जानकारी",
        "Contact": "संपर्क", "Achievements": "उपलब्धियाँ",
    },
    "zh": {
        "Summary": "个人简介", "Experience": "工作经历", "Education": "教育背景",
        "Skills": "专业技能", "Languages": "语言能力", "Projects": "项目经历",
        "Certifications": "证书", "Awards": "获奖荣誉", "Interests": "兴趣爱好",
        "Volunteering": "志愿经历", "Publications": "发表作品",
        "Courses": "培训课程", "References": "推荐人",
        "Additional information": "补充信息",
        "Contact": "联系方式", "Achievements": "主要成就",
    },
    "ja": {
        "Summary": "職務要約", "Experience": "職務経歴", "Education": "学歴",
        "Skills": "スキル", "Languages": "語学", "Projects": "プロジェクト",
        "Certifications": "資格", "Awards": "受賞歴", "Interests": "趣味",
        "Volunteering": "ボランティア", "Publications": "出版物",
        "Courses": "研修", "References": "推薦状",
        "Additional information": "補足情報",
        "Contact": "連絡先", "Achievements": "実績",
    },
    "ko": {
        "Summary": "프로필", "Experience": "경력", "Education": "학력",
        "Skills": "기술", "Languages": "언어", "Projects": "프로젝트",
        "Certifications": "자격증", "Awards": "수상", "Interests": "관심사",
        "Volunteering": "봉사 활동", "Publications": "출판물",
        "Courses": "교육 과정", "References": "추천인",
        "Additional information": "추가 정보",
        "Contact": "연락처", "Achievements": "성과",
    },
}


def supported_locales() -> list[str]:
    return sorted(HEADING_TRANSLATIONS)


def translate_heading(locale: str, heading: str) -> str:
    """Translate a canonical English heading, falling back to English."""
    table = HEADING_TRANSLATIONS.get((locale or "en").lower())
    if not table:
        return heading
    return table.get(heading, heading)


def translate_headings(locale: str, headings: list[str] | None = None) -> dict[str, str]:
    """Return a ``{english: localised}`` mapping for the requested headings."""
    keys = headings or HEADING_KEYS
    return {key: translate_heading(locale, key) for key in keys}

