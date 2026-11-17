-- Schema for the shared multi-tenant mini-ERP.
-- Every business table carries tenant_id: this is the "one shared stack" model.

CREATE TABLE tenants (
    id         int PRIMARY KEY,
    name       text NOT NULL,
    plan       text NOT NULL,              -- 'small' | 'enterprise'
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE orders (
    id         bigserial PRIMARY KEY,
    tenant_id  int  NOT NULL REFERENCES tenants(id),
    order_date date NOT NULL,
    status     text NOT NULL DEFAULT 'new',
    total      numeric(14,2) NOT NULL DEFAULT 0
);
CREATE INDEX orders_tenant_date_idx ON orders (tenant_id, order_date);

CREATE TABLE order_lines (
    id         bigserial PRIMARY KEY,
    tenant_id  int    NOT NULL REFERENCES tenants(id),
    order_id   bigint NOT NULL REFERENCES orders(id),
    product    text   NOT NULL,
    qty        int    NOT NULL,
    unit_price numeric(12,2) NOT NULL
);
CREATE INDEX order_lines_tenant_order_idx ON order_lines (tenant_id, order_id);
