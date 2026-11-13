create database finance_dashboard;
use finance_dashboard;


CREATE TABLE categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50),
    category_flag BOOLEAN
);


create table accounts (
	account_id int auto_increment primary key,
    account_name varchar(30),
    account_type ENUM('bank', 'broker', 'mf_folio', 'cash', 'aa_sandbox'),
    source ENUM ('csv_import', 'cas_import', 'aa_fetch', 'manual'),
    current_balance decimal(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

create table transactions (
	transaction_id int auto_increment primary key,
    account_id int,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id),
    category_id int,
	FOREIGN KEY (category_id) REFERENCES categories(category_id),
    amount decimal(12,2),
    transaction_date DATE,
    description varchar(100),
    merchant varchar(50),
    txn_type ENUM('debit' , 'credit'),
    is_recurring boolean
);

create table budgets (
	budget_id int auto_increment primary key,
    category_id int,
    foreign key (category_id) references categories(category_id),
    month_year DATE,
    budget_limit decimal (12,2)
);

create table holdings(
	holding_id int auto_increment primary key,
    account_id int,
    foreign key (account_id) references accounts(account_id),
    instrument_name varchar(50),
    instrument_type Enum('stocks','mf'),
    quantity decimal(12,3),
    avg_buy_price decimal(12,2),
    current_price decimal(12,2),
    isin varchar(12),
    folio_number varchar(30)
);

create table consent_log (
	consent_id int auto_increment primary key,
    fip_name varchar(50),
    consent_status ENUM ('pending','approved','rejected','expired'),
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL
);

create table import_log (
	import_id int auto_increment primary key,
    account_id int,
    foreign key (account_id) references accounts(account_id),
    import_type ENUM('bank','stock','mf'),
    number_rows_added int,
    duplicate_rows int,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
















