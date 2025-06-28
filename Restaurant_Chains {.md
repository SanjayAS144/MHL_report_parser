Restaurant_Chains {
int chain_id PK
string chain_name
string chain_code
string business_type
datetime created_at
datetime updated_a
}
    
Brands {
int brand_id PK
string brand_name
string brand_code
string cuisine_type
string brand_category
string brand_description
string logo_url
boolean active_status
datetime created_at
datetime updated_at
}

Outlets {
int outlet_id PK
int chain_id FK
string outlet_name
string outlet_code
string location_address
string city
string state
string pincode
string phone
string email
string outlet_type
string gstin
boolean active_status
datetime created_at
datetime updated_at
}

Outlet_Brands {
int outlet_brand_id PK
int outlet_id FK
int brand_id FK
string brand_outlet_code
boolean active_status
date start_date
date end_date
datetime created_at
datetime updated_at
}

Partners {
int partner_id PK
string partner_name
string partner_code
string api_endpoint
string settlement_frequency
json commission_structure
boolean active_status
datetime created_at
datetime updated_at
}

Partner_Outlets {
int partner_outlet_id PK
int partner_id FK
int outlet_id FK
string partner_restaurant_id
string partner_restaurant_name
string subzone
date onboarding_date
string status
datetime created_at
datetime updated_at
}

Customers {
int customer_id PK
string partner_customer_id
int partner_id FK
string phone
string email
string customer_type
boolean is_gold_member
boolean is_swiggy_one
datetime created_at
datetime updated_at
}

Order_Sources {
int source_id PK
string source_name
string source_type
datetime created_at
datetime updated_at
}

Orders {
int order_id PK
string original_order_id
string pos_order_id
int source_id FK
int partner_id FK
int outlet_id FK
int outlet_brand_id FK
int customer_id FK
date order_date
time order_time
string order_status
string order_type
string delivery_type
string payment_type
decimal order_value
datetime created_at
datetime updated_at
}

Order_Items {
int order_item_id PK
int order_id FK
string item_name
string item_category
string variation
string hsn_code
int quantity
decimal unit_price
decimal total_price
string item_status
int preparation_time_mins
datetime created_at
}

Payments {
int payment_id PK
int order_id FK
string payment_type
string payment_status
decimal payment_amount
string payment_gateway
string transaction_id
datetime payment_date
string refund_status
decimal refund_amount
datetime refund_date
datetime created_at
datetime updated_at
}

Invoices {
int invoice_id PK
int order_id FK
string invoice_type
string invoice_number
date invoice_date
string invoice_status
decimal total_amount
decimal tax_amount
decimal net_amount
datetime created_at
datetime updated_at
}

Order_Financial_Details {
int financial_detail_id PK
int order_id FK
decimal gross_order_value
decimal platform_commission
decimal cgst_amount
decimal sgst_amount
decimal igst_amount
decimal merchant_gst
decimal ecommerce_gst
decimal tds_amount
decimal net_payout_to_restaurant
date settlement_date
datetime created_at
datetime updated_at
}

Discounts_Applied {
int discount_id PK
int order_id FK
string discount_type
string discount_name
decimal discount_amount
decimal discount_percentage
decimal discount_cap
string discount_sponsored_by
string voucher_code
string campaign_id
datetime created_at
}

Customer_Feedback {
int feedback_id PK
int order_id FK
int customer_id FK
int rating
text review_text
string complaint_tag
string complaint_type
string complaint_status
datetime feedback_date
datetime created_at
}

Order_Reconciliation {
int reconciliation_id PK
int order_id FK
string platform_order_id
string pos_order_id
string reconciliation_status
decimal platform_amount
decimal pos_amount
decimal difference_amount
date reconciliation_date
datetime created_at
datetime updated_at
}

Settlement_Reports {
int settlement_id PK
int partner_id FK
int outlet_id FK
date settlement_period_start
date settlement_period_end
int total_orders
decimal total_revenue
decimal total_commission
decimal total_deductions
decimal total_adjustments
decimal net_settlement_amount
string settlement_status
date settlement_date
datetime created_at
datetime updated_at
}

Daily_Metrics {
int metric_id PK
int partner_id FK
int outlet_id FK
date metric_date
int total_orders
decimal total_sales
decimal avg_order_value
decimal total_discounts_given
decimal customer_ratings_avg
int total_complaints
decimal online_percentage
decimal offline_hours
decimal kpt_minutes
datetime created_at
}

Marketing_Campaigns {
int campaign_id PK
int partner_id FK
int outlet_id FK
string campaign_name
string campaign_type
date start_date
date end_date
decimal budget_spent
int impressions
int clicks
int orders_generated
decimal revenue_generated
decimal roi
datetime created_at
datetime updated_at
}