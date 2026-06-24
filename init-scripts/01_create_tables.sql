CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    client_id UUID NOT NULL,
    client_name VARCHAR(100) NOT NULL,
    transaction_date DATE NOT NULL,
    description VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    type VARCHAR(10) NOT NULL CHECK (type IN ('debito', 'credito')),
    amount DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    establishment VARCHAR(150),
    balance_after DECIMAL(12, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    client_id UUID UNIQUE NOT NULL,
    client_name VARCHAR(100) NOT NULL,
    account_number VARCHAR(20) NOT NULL,
    agency VARCHAR(10) NOT NULL,
    balance DECIMAL(12, 2) NOT NULL DEFAULT 0,
    overdraft_limit DECIMAL(12, 2) NOT NULL DEFAULT 0,
    account_type VARCHAR(20) NOT NULL DEFAULT 'corrente',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO accounts (client_id, client_name, account_number, agency, balance, overdraft_limit, account_type) VALUES
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'Maria Silva', '12345-6', '0001', 4520.75, 2000.00, 'corrente'),
('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'João Santos', '78901-2', '0001', 1230.40, 1000.00, 'corrente'),
('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 'Ana Oliveira', '34567-8', '0042', 8750.00, 5000.00, 'corrente');

INSERT INTO transactions (client_id, client_name, transaction_date, description, category, type, amount, payment_method, establishment, balance_after) VALUES
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'Maria Silva', '2026-06-23', 'Compra Drogaria São Paulo', 'farmacia', 'debito', 87.50, 'debito', 'Drogaria São Paulo - Unidade Centro', 4520.75),
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'Maria Silva', '2026-06-22', 'Supermercado Extra', 'mercado', 'debito', 342.18, 'credito', 'Extra Hipermercado - Pinheiros', 4608.25),
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'Maria Silva', '2026-06-21', 'Posto Shell Av. Paulista', 'gasolina', 'debito', 215.00, 'debito', 'Posto Shell - Av. Paulista 1500', 4950.43),
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'Maria Silva', '2026-06-20', 'iFood Restaurante', 'alimentacao', 'debito', 56.90, 'credito', 'iFood - Restaurante Sabor Caseiro', 5165.43),
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'Maria Silva', '2026-06-19', 'Netflix Assinatura', 'assinatura', 'debito', 39.90, 'credito', 'Netflix Serviços Digitais', 5222.33),
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'Maria Silva', '2026-06-18', 'PIX Recebido - Salário', 'renda', 'credito', 6500.00, 'pix', NULL, 5262.23),
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'Maria Silva', '2026-06-17', 'Conta de Luz ENEL', 'moradia', 'debito', 189.50, 'boleto', 'ENEL Distribuição SP', -1237.77),
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'Maria Silva', '2026-06-15', 'Uber Viagem', 'transporte', 'debito', 32.40, 'credito', 'Uber do Brasil', -1048.27),

('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'João Santos', '2026-06-23', 'Mercado Pão de Açúcar', 'mercado', 'debito', 178.90, 'debito', 'Pão de Açúcar - Moema', 1230.40),
('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'João Santos', '2026-06-22', 'Farmácia Raia', 'farmacia', 'debito', 45.60, 'debito', 'Droga Raia - Unidade Vila Mariana', 1409.30),
('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'João Santos', '2026-06-21', 'Posto Ipiranga BR', 'gasolina', 'debito', 180.00, 'debito', 'Posto Ipiranga - Rua Augusta', 1454.90),
('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'João Santos', '2026-06-20', 'Spotify Premium', 'assinatura', 'debito', 21.90, 'credito', 'Spotify AB', 1634.90),
('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'João Santos', '2026-06-19', 'Aluguel Apartamento', 'moradia', 'debito', 1800.00, 'boleto', 'Imobiliária Lopes', 1656.80),
('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'João Santos', '2026-06-18', 'PIX Recebido - Freelance', 'renda', 'credito', 2200.00, 'pix', NULL, 3456.80),
('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'João Santos', '2026-06-16', 'Rappi Mercado', 'mercado', 'debito', 95.30, 'credito', 'Rappi - Mercado Express', 1256.80),
('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'João Santos', '2026-06-14', 'Cinema Cinemark', 'lazer', 'debito', 62.00, 'debito', 'Cinemark - Shopping Ibirapuera', 1352.10),

('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 'Ana Oliveira', '2026-06-23', 'Posto BR Rede', 'gasolina', 'debito', 250.00, 'debito', 'Posto BR - Rod. Raposo Tavares', 8750.00),
('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 'Ana Oliveira', '2026-06-22', 'Atacadão Compras', 'mercado', 'debito', 520.45, 'debito', 'Atacadão - Unidade Osasco', 9000.00),
('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 'Ana Oliveira', '2026-06-21', 'Drogasil Medicamentos', 'farmacia', 'debito', 132.80, 'credito', 'Drogasil - Shopping Eldorado', 9520.45),
('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 'Ana Oliveira', '2026-06-20', 'Amazon Prime', 'assinatura', 'debito', 14.90, 'credito', 'Amazon Serviços', 9653.25),
('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 'Ana Oliveira', '2026-06-19', 'PIX Recebido - Salário', 'renda', 'credito', 9800.00, 'pix', NULL, 9668.15),
('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 'Ana Oliveira', '2026-06-18', 'Condomínio Residencial', 'moradia', 'debito', 850.00, 'boleto', 'Cond. Res. Jardins', -131.85),
('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 'Ana Oliveira', '2026-06-17', 'Academia SmartFit', 'saude', 'debito', 99.90, 'debito', 'Smart Fit - Unidade Faria Lima', 718.15),
('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 'Ana Oliveira', '2026-06-15', 'Restaurante Outback', 'alimentacao', 'debito', 185.00, 'credito', 'Outback Steakhouse - Morumbi', 818.05);
