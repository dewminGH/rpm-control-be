CREATE TABLE Users (
    user_id serial PRIMARY KEY,
    user_name VARCHAR(255),
    device_secret VARCHAR(255),
    constraint c1 foreign key (device_secret)
references fan_rpms(id)
);

drop table Users

create table fan_rpms(
id varchar(255) PRIMARY key,
fan_speed float,
time date,
temperature float,
humidity float,
light float,
cO2 float,
container_type varchar(255)
);


drop table fan_rpms

insert into Users (user_name) values ('test-1')

select * from fanRpms

insert into fan_rpms (id,
fan_speed ,
time ,
temperature ,
humidity ,
light ,
cO2,
container_type) values ('ds-2',1400 ,'2025-08-13',30,1300,1300,1300,'apple') 

