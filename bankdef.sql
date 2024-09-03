create database bank; 
use bank;
create table customer(
    user_id int(10) primary key, 
    name varchar(20) not null, 
    gender varchar(10) CHECK(gender in ('Male','Female')) not null,
    age int(3) not null,
    bal int(10) not null, 
    date_joined date not null, 
    passcode char(10) not null);

create table transact(
    t_id int(10) primary key,
    user_id int(10) not null, 
    tdate date not null, 
    ttime time not null,
    credit int(10), 
    debit int(10),
    payee_recipient int(10) not null,
    foreign key (user_id) references customer(user_id));

-- to run the code, please run SOURCE C:\Users\shiva\OneDrive\Desktop\computer_proj\bankdef.sql