"""
Xodimning 'User/Employee ID' maydonidan lavozim, mobil raqam, ofis raqami va ichki raqam
ma'lumotlarini ajratib olish (parse) moduli.

Qo'llab-quvvatlanadigan ajratuvchi belgilar:
  /   @   #   $   %   |

Format:
  Lavozim / Mobil raqam / Ofis raqami / Ichki raqam
Misollar:
  - Buxgalter / +998 93399 33 31 / 77 612 50 11 / 80-11
  - Obodonlashtirish,bino va inshoatlarga xizmat ko'rsatish bo'limi boshlig'i / +998 93 892 37 37 / 80-58
  - Bosh energetik / +998 90 123 45 67 / 105
  - Xodim / 80-58
"""
import re

def is_internal_number(val: str) -> bool:
    """
    4 talik ichki raqamlar (masalan: '80 10', '80-45', '8011') hamda 2-6 xonali qisqa ATS raqamlari
    avtomatik ichki raqam (IP telefon / ichki ATS) deb tan olinadi.
    Agar raqam '+' bilan boshlansa, bu mobil raqam hisoblanadi.
    """
    if not val or not str(val).strip():
        return False
    clean_val = str(val).strip()
    if clean_val.startswith('+'):
        return False
    digits = re.sub(r'\D', '', clean_val)
    # Ichki raqamlar 4 ta raqamdan (hamda 2-6 xonali) iborat
    return len(digits) in (2, 3, 4, 5, 6)

def is_office_number(val: str) -> bool:
    """
    Faqatgina 75 (Qashqadaryo) va 71 (Toshkent) kodli raqamlar hamda
    7 talik shahar raqamlari ofis raqami hisoblanadi:
    - '+998 75 xxx xx xx' yoki '75 xxx xx xx'
    - '+998 71 xxx xx xx' yoki '71 xxx xx xx'
    - '612 50 11' kabi 7 talik shahar raqamlari

    Eslatma: +998 77 xxx xx xx mobil raqam hisoblanadi!
    """
    if not val or not str(val).strip():
        return False
    clean_val = str(val).strip()
    digits = re.sub(r'\D', '', clean_val)
    if not digits:
        return False

    # 12 xonali (+998 bilan): faqatgina 75 va 71 kodlari ofis raqami!
    if len(digits) == 12 and digits.startswith('998'):
        nat = digits[3:]
        return nat.startswith(('75', '71'))

    # 9 xonali: faqatgina 75 va 71 bilan boshlansa ofis raqami!
    if len(digits) == 9:
        return digits.startswith(('75', '71'))

    # 7 xonali shahar raqamlari (masalan: 612 50 11)
    if len(digits) == 7 and not clean_val.startswith('+'):
        return True

    return False

def normalize_val(val: str, default: str = "—") -> str:
    if not val or not str(val).strip():
        return default
    s = str(val).strip()
    if s.lower() in ("-", "--", "—", "none", "yo'q", "yoq", "null"):
        return default
    return s

def parse_employee_id(raw_str: str) -> dict:
    if not raw_str or not str(raw_str).strip():
        return {
            "position": "—",
            "phone": "—",
            "office_phone": "—",
            "ip_phone": "—",
            "raw_info": ""
        }
    
    clean = str(raw_str).strip()
    
    # Har qanday belgilangan ajratuvchilar: / @ # $ % | va ularning atrofidagi probellar
    parts = [p.strip() for p in re.split(r'\s*[/@#$%|]+\s*', clean) if p.strip()]
    
    if not parts:
        return {
            "position": "—",
            "phone": "—",
            "office_phone": "—",
            "ip_phone": "—",
            "raw_info": clean
        }
        
    position = parts[0]
    nums = list(parts[1:])
    phone = "—"
    office_phone = "—"
    ip_phone = "—"
    
    # 1. Ichki raqamni aniqlash (4 talik yoki 2-6 talik)
    for n in list(nums):
        if is_internal_number(n):
            ip_phone = n
            nums.remove(n)
            break
            
    # 2. Ofis raqamini aniqlash (9 talik yoki 7 talik (+)siz)
    for n in list(nums):
        if is_office_number(n):
            office_phone = n
            nums.remove(n)
            break
            
    # 3. Mobil raqamni aniqlash (qolgan raqamlar yoki + bilan boshlanadigan)
    for n in list(nums):
        phone = n
        nums.remove(n)
        break
        
    return {
        "position": normalize_val(position),
        "phone": normalize_val(phone),
        "office_phone": normalize_val(office_phone),
        "ip_phone": normalize_val(ip_phone),
        "raw_info": clean
    }

def parse_employee_template(text: str) -> dict:
    """
    Foydalanuvchi yuborgan shablon matnidan xodim ma'lumotlarini ajratib oladi:
    👤 F.I.SH: Eshmatov Toshmat
    💼 Lavozimi: Bosh muhandis
    📧 Pochta manzili: t.eshmatov@uz-potash.uz
    📱 Mobil raqam: +998901234567
    🏢 Ofis raqami: 612 50 11
    ☎️ Ichki raqam: 80 11 (yoki 80-58)
    """
    res = {
        "name": "",
        "position": "",
        "email": "",
        "phone": "",
        "office_phone": "",
        "ip_phone": ""
    }
    if not text:
        return res

    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    for line in lines:
        clean_line = re.sub(r'^[👤💼📧📱🏢📞☎️🟢\*\-_•\s]+', '', line).strip()
        if ':' in clean_line:
            key, val = clean_line.split(':', 1)
            key_lower = key.strip().lower()
            val_clean = val.strip()

            if any(k in key_lower for k in ['f.i.sh', 'fish', 'ism', 'fio', 'name']):
                res['name'] = val_clean
            elif any(k in key_lower for k in ['lavozim', 'position', 'mutaxassis']):
                res['position'] = val_clean
            elif any(k in key_lower for k in ['pochta', 'email', 'mail']):
                res['email'] = val_clean
            elif any(k in key_lower for k in ['ofis', 'office']):
                res['office_phone'] = val_clean
            elif any(k in key_lower for k in ['ichki', 'ip']):
                res['ip_phone'] = val_clean
            elif any(k in key_lower for k in ['mobil', 'telefon', 'tel', 'phone', 'aloqa']):
                res['phone'] = val_clean

    # Agar mobil raqam deb kiritilgan qiymat 4 yoki 6 talik ichki raqam bo'lsa
    if res['phone'] and is_internal_number(res['phone']) and not res['ip_phone']:
        res['ip_phone'] = res['phone']
        res['phone'] = ""
    elif res['phone'] and is_office_number(res['phone']) and not res['office_phone']:
        res['office_phone'] = res['phone']
        res['phone'] = ""

    # Agar email qatorida topilmagan bo'lsa, butun matndan email qidiramiz
    if not res['email']:
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        if email_match:
            res['email'] = email_match.group(0).strip()

    # Agar email domenisiz kiritilgan bo'lsa (masalan t.eshmatov)
    if res['email'] and '@' not in res['email']:
        res['email'] = f"{res['email']}@uz-potash.uz"

    return res
