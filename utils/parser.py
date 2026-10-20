"""
Xodimning 'User/Employee ID' maydonidan lavozim, mobil raqam, ofis raqami va ichki raqam
ma'lumotlarini ajratib olish (parse) moduli.

Qo'llab-quvvatlanadigan ajratuvchi belgilar:
  /   @   #   $   %   |

Format:
  Lavozim / Mobil raqam / Ofis raqami / Ichki raqam
Misollar:
  - Buxgalter / +998 93399 33 31 / 612 50 11 / 80 11
  - Obodonlashtirish,bino va inshoatlarga xizmat ko'rsatish bo'limi boshlig'i / +998 93 892 37 37 / 80-58
  - Bosh energetik / +998 90 123 45 67 / 105
  - Xodim / 80-58
"""
import re

def is_internal_number(val: str) -> bool:
    """
    4 talik yoki 6 talik (hamda 2-6 xonali qisqa) raqamlar avtomatik
    ichki raqam (IP telefon / ichki ATS) deb tan olinadi.
    Masalan: '80-58', '8011', '105', '12-34-56', '805812'.
    Agar raqam '+' bilan boshlansa, bu xalqaro/mobil raqam hisoblanadi.
    """
    if not val or not str(val).strip():
        return False
    clean_val = str(val).strip()
    if clean_val.startswith('+'):
        return False
    digits = re.sub(r'\D', '', clean_val)
    # 4 talik va 6 talik (hamda 2-6 ta raqamdan iborat) ichki raqamlar
    return len(digits) in (2, 3, 4, 5, 6)

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
    phone = "—"
    office_phone = "—"
    ip_phone = "—"
    
    if len(parts) == 2:
        val = parts[1]
        digits_only = re.sub(r'\D', '', val)
        if is_internal_number(val):
            # 4 talik yoki 6 talik ichki raqam
            ip_phone = val
        elif len(digits_only) == 7 and not val.startswith('+'):
            # 7 talik shahar ofis raqami
            office_phone = val
        else:
            # Mobil raqam
            phone = val

    elif len(parts) == 3:
        p1 = parts[1]
        p2 = parts[2]
        
        # 3-qism tekshiriladi: 4 talik yoki 6 talik bo'lsa -> auto ichki raqam!
        if is_internal_number(p2):
            ip_phone = p2
            # 2-qism ofis raqamimi yoki mobil raqam?
            digits_p1 = re.sub(r'\D', '', p1)
            if len(digits_p1) == 7 and not p1.startswith('+'):
                office_phone = p1
            else:
                phone = p1
        else:
            # 3-qism 7 xonali yoki boshqa ofis raqami bo'lsa
            phone = p1
            office_phone = p2

    elif len(parts) >= 4:
        phone = parts[1]
        p2 = parts[2]
        p3 = parts[3]
        
        # Agar 3-qism ichki raqam, 4-qism ofis raqami qilib kiritilgan bo'lsa
        if is_internal_number(p2) and not is_internal_number(p3):
            office_phone = p3
            ip_phone = p2
        else:
            office_phone = p2
            ip_phone = p3
        
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
        clean_line = re.sub(r'^[👤💼📧📱🏢📞☎️\*\-_•\s]+', '', line).strip()
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

    # Agar email qatorida topilmagan bo'lsa, butun matndan email qidiramiz
    if not res['email']:
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        if email_match:
            res['email'] = email_match.group(0).strip()

    # Agar email domenisiz kiritilgan bo'lsa (masalan t.eshmatov)
    if res['email'] and '@' not in res['email']:
        res['email'] = f"{res['email']}@uz-potash.uz"

    return res
