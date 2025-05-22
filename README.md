Kaip paleisti programą:
1. Nusiklonuokite projektą vykdydami šią komandą:
g i t c l o n e h t t p s : / / g i t h u b . com / j o g i s 8 6 8 / cardgame . g i t
2. Pereikite į katalogą cardgame:
cd cardgame
3. Sukurkite virtualią Python aplinką ir ją aktyvuokite:
• Linux / macOS:
p y t h o n 3 −m venv venv
s o u r c e venv / b i n / a c t i v a t e
• Windows:
p y t h o n −m venv venv
venv \ S c r i p t s \ a c t i v a t e . b a t
4. Įdiekite reikalingas priklausomybes:
p i p i n s t a l l − r r e q u i r e m e n t s . t x t
5. Jei reikia, papildomai įdiekite Django:
p i p i n s t a l l Django
6. Sukurkite duomenų bazės lenteles:
p y t h o n manage . py m i g r a t e
7. Paleiskite serverį:
p y t h o n manage . py r u n s e r v e r
8. Naršyklėje atidarykite adresą: http://127.0.0.1:8000/

