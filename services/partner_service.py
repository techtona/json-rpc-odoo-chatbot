# services/partner_service.py
from client import OdooRPCClient

class PartnerService:
    def __init__(self):
        self.client = OdooRPCClient()

    def get_customer_by_email(self, email):
        domain = [[['email', '=', email]]]
        fields = ['id', 'name', 'email', 'phone']
        result = self.client.execute_kw('res.partner', 'search_read', domain, {'fields': fields, 'limit': 1})
        return result[0] if result else None

    def get_all_customers(self, limit=10):
        # domain = [[['customer_rank', '>', 0]]]
        domain = [[]]
        fields = ['id', 'name', 'email', 'phone_sanitized']
        return self.client.execute_kw('res.partner', 'search_read', domain, {'fields': fields, 'limit': limit})

    def get_aged_receivables_from_customer(self, customer_phone):
        partner = self.client.execute_kw(
            'res.partner', 'search_read',
            [[['phone_sanitized', '=', customer_phone]]],
            {'fields': ['id', 'name'], 'limit': 1}
        )

        print(partner)

        if partner:
            partner_id = partner[0]['id']

            # Step 2: Ambil invoice berdasarkan partner_id
            invoices = self.client.execute_kw(
                'account.move', 'search_read',
                [[
                    ['partner_id', '=', partner_id],
                    ['move_type', '=', 'out_invoice'],
                    ['state', '=', 'posted']
                ]],
                {'fields': ['name', 'amount_total', 'amount_residual']}
            )

            for inv in invoices:
                print(inv)
    
    def get_customer_by_id(self, customer_id):
        domain = [[['id', '=', customer_id]]]
        fields = ['id', 'name', 'email', 'phone']
        result = self.client.execute_kw('res.partner', 'search_read', domain, {'fields': fields, 'limit': 1})
        return result[0] if result else None