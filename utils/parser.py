"""
Xodimning 'User/Employee ID' maydonidan lavozim, mobil raqam, ofis raqami va ichki raqam
ma'lumotlarini ajratib olish (parse) moduli.

Qo'llab-quvvatlanadigan ajratuvchi belgilar:
  /   @   #   $   %   |

Format:
  Lavozim / Mobil raqam / Ofis raqami / Ichki raqam
Misol:
  Buxgalter / +998 93399 33 31 / 612 50 11 / 80 11
"""
import re

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
        if len(digits_only) <= 4 and not val.startswith('+'):
            ip_phone = val
        else:
            phone = val
    elif len(parts) == 3:
        phone = parts[1]
        p2 = parts[2]
        digits_p2 = re.sub(r'\D', '', p2)
        # Agar 3-qism 4 ta yoki undan kam raqamdan iborat bo'lsa (masalan 105, 8011), bu ichki raqam
        if len(digits_p2) <= 4 and not p2.startswith('+'):
            ip_phone = p2
        else:
            office_phone = p2
    elif len(parts) >= 4:
        phone = parts[1]
        office_phone = parts[2]
        ip_phone = parts[3]
        
    return {
        "position": position,
        "phone": phone,
        "office_phone": office_phone,
        "ip_phone": ip_phone,
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
    ☎️ Ichki raqam: 80 11
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

    # Agar email qatorida topilmagan bo'lsa, butun matndan email qidiramiz
    if not res['email']:
        email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        if email_match:
            res['email'] = email_match.group(0).strip()

    # Agar email domenisiz kiritilgan bo'lsa (masalan t.eshmatov)
    if res['email'] and '@' not in res['email']:
        res['email'] = f"{res['email']}@uz-potash.uz"

    return res
