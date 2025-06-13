# main.py
from services.partner_service import PartnerService

if __name__ == "__main__":
    service = PartnerService()

    print("🔍 List customer:")
    customers = service.get_all_customers(limit=5)
    for c in customers:
        print(f"{c['id']} . {c['name']} - {c['phone_sanitized']} - {c['email']}")

    print("\n🔎 Cari berdasarkan phone number: +6281321397270")
    customer_ar = service.get_aged_receivables_from_customer("+6281321397270")
    
    if customer_ar:
        print("\n📋 Aged Receivables:")
        print(customer_ar)
    else:
        print("Aged Receivable Customer tidak ditemukan.")
