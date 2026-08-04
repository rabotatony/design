# המכשיר — הוכחת פעולה (composer.py)

## מה זה

composer.py הוא המכשיר: מקבל DNA של תחום, מוציא מערכת עיצוב שלמה
(tokens.css + layout.css + motion.css). שושנה היא קלט אחד — לא המטרה.

## הפרדת כוחות

- PRINCIPLES — אינטליגנציית העיצוב של המכשיר (קבועה, כללית):
  משטחים מהחומר, צללים צבועים במקור האור, רדיוסים לפי תפקיד,
  מרווחי האצלה, קצב נשימה, grain מהחומר.
- MATERIALS — בסיס ידע פיזיקלי: קלף, דיו, לילה, אבן, מים, עץ, מתכת, עשן.
- DNA — החומר של הפרויקט עצמו (identity_extractor).
- manifest — כל שורת פלט מקושרת ל-(שורש DNA, עיקרון).

## הוכחה 1: שושנה

- materials_detected: parchment, ink, night, metal
- anchors_from_dna: 3 (מ-palette_logic)
- rhythm: 1.6s / 2.8s / 3.2s (4:7:8 פורס)
- signature_radius: 16px 6px 16px 6px (גאומטריית עלה)
- emanation_layout: true
- clean_score: 1.0 | tells: 0 | determinism: PASS

## הוכחה 2: הכללה (דומיין אחר — מצפה כוכבים)

- materials_detected: night, stone
- surface-0: #181c2e (לילה, לא קלף)
- ink: #d8dde8 (כסף, לא דיו)
- signature_radius: 999px 4px 999px 4px (גאומטריית גלגל)
- rhythm: 2.0s / 0.8s / 2.0s (גאות 5:2:5)
- clean_score: 1.0 | tells: 0
- fingerprint שונה משושנה: PASS

אותו מכשיר, שני דומיינים, שתי מערכות שונות לחלוטין, שתיהן נקיות.

## מה המכשיר עדיין לא יודע (החזית, בכנות)

1. גזירת DNA אוטומטית מפרויקט קיים — כרגע DNA נכתב/מאומת ידנית.
   identity_extractor צריך ללמוד לקרוא codebase + תוכן ולהציע DNA.
2. גאומטריית חתימה כללית — המכשיר מזהה petal/wheel/flame;
   מחוות אחרות מסומנות human-input-needed (בכוונה).
3. החלה על עמודים קיימים — composer מייצר מערכת; ההחלה על
   קומפוננטות קיימות דורשת apply ברמת CSS (קיים חלקית).
4. טקסט מקורי מאפס — נשאר מחוץ לשכבות האוטומטיות (כלל ברזל 3).

## השורה התחתונה

השינוי בשושנה (ובכל פרויקט) עובר מעכשיו דרך המכשיר:
DNA → composer → בדיקת clean_score → החלה. לא ידנית.