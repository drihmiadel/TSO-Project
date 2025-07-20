# src/transliteration_engine.py

# هذا الملف يحتوي على منطق النقحرة الفعلي، بما في ذلك التعامل مع
# القواعد الأساسية والأكاديمية، والقواعد المخصصة، ومعالجة المدود،
# والتحويل العكسي.

from .transliteration_rules import BASIC_TRANSLITERATION_MAP, ACADEMIC_TRANSLITERATION_MAP, \
    REVERSE_BASIC_TRANSLITERATION_MAP, REVERSE_ACADEMIC_TRANSLITERATION_MAP, \
    load_custom_profile_rules
import re

class TransliterationEngine:
    def __init__(self, mode="basic", custom_profile_path=None):
        """
        تهيئة محرك النقحرة.
        :param mode: "basic" للوضع البسيط، "academic" للوضع الأكاديمي.
        :param custom_profile_path: مسار لملف JSON لقواعد مخصصة (اختياري).
        """
        self.mode = mode
        self.to_latin_map = {}
        self.from_latin_map = {}
        self._initialize_maps()
        if custom_profile_path:
            self.load_custom_rules(custom_profile_path)

    def _initialize_maps(self):
        """تهيئة خرائط النقحرة بناءً على الوضع."""
        if self.mode == "basic":
            self.to_latin_map = BASIC_TRANSLITERATION_MAP
            self.from_latin_map = REVERSE_BASIC_TRANSLITERATION_MAP
        elif self.mode == "academic":
            self.to_latin_map = ACADEMIC_TRANSLITERATION_MAP
            self.from_latin_map = REVERSE_ACADEMIC_TRANSLITERATION_MAP
        else:
            raise ValueError("الوضع غير صالح. يجب أن يكون 'basic' أو 'academic'.")

        # فرز خريطة التحويل العكسي حسب طول المفتاح تنازلياً
        # هذا يضمن مطابقة الأحرف المركبة (مثل 'sh') قبل الأحرف الفردية ('s')
        self.from_latin_map = dict(sorted(self.from_latin_map.items(), key=lambda item: len(item[0]), reverse=True))


    def load_custom_rules(self, profile_path):
        """تحميل وتطبيق قواعد مخصصة من ملف JSON."""
        custom_to_latin, custom_from_latin = load_custom_profile_rules(profile_path)
        self.to_latin_map.update(custom_to_latin)
        # تحديث الخريطة العكسية وفرزها مرة أخرى
        self.from_latin_map.update(custom_from_latin)
        self.from_latin_map = dict(sorted(self.from_latin_map.items(), key=lambda item: len(item[0]), reverse=True))
        print(f"تم تحميل القواعد المخصصة من: {profile_path}")

    def transliterate(self, text):
        """
        نقحرة النص العربي/السامي إلى اللاتيني.
        :param text: النص الأصلي.
        :return: النص المنقحر.
        """
        result = []
        i = 0
        while i < len(text):
            char = text[i]
            transliterated_char = self.to_latin_map.get(char, char) # استخدام الحرف نفسه إذا لم توجد قاعدة
            result.append(transliterated_char)
            i += 1

        # معالجة خاصة للحركات والتشكيل في الوضع الأكاديمي إذا كان مطلوباً
        # (يمكن إضافة منطق أكثر تعقيداً هنا لمعالجة المدود والجذور)

        # مثال على معالجة المدود (تبسيط):
        # و بعد حرف بفتحة -> wa
        # و بعد حرف بضمة -> wu / ū
        # ي بعد حرف بكسرة -> yi / ī

        # هذا يتطلب تحليل سياقي متقدم، ويمكن أن يتم في مرحلة لاحقة.
        # للآن، القواعد الأساسية في الخرائط كافية.

        return "".join(result)

    def reverse_transliterate(self, transliterated_text):
        """
        تحويل النص المنقحر (اللاتيني) إلى العربي/السامي.
        يتطلب هذا معالجة متقدمة للغموض والأحرف المركبة.
        :param transliterated_text: النص المنقحر باللاتينية.
        :return: النص المحول إلى العربي.
        """
        result = []
        i = 0
        while i < len(transliterated_text):
            matched = False
            # حاول مطابقة أطول الأحرف أولاً (مثل 'sh' قبل 's')
            for latin_seq, arabic_char in self.from_latin_map.items():
                if transliterated_text[i:].startswith(latin_seq):
                    result.append(arabic_char)
                    i += len(latin_seq)
                    matched = True
                    break
            if not matched:
                result.append(transliterated_text[i]) # أضف الحرف كما هو إذا لم يتم العثور على قاعدة
                i += 1
        return "".join(result)
