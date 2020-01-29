drop table if exists JUR_SETTINGS, JUR_PROFILE, DISCOVERY, DINO, DINO_SEEING, DISCOVERY_ASSIST;


create table JUR_SETTINGS(
    discovery_reward    bigint,
    assist_reward       bigint,
    seeing_reward       bigint,
    crowd_multiplier    float
);

create table JUR_PROFILE(
    member_id bigint,
    guild_id bigint,
    experience float default 0,

    primary key (member_id)
);

create table DINO(
    name            varchar(40),
    link_pl         varchar(40),
    link_en         varchar(40),
    image_path      varchar(40),

    primary key (name)
);

create table DISCOVERY(
    id          bigint auto_increment,
    dino_name   varchar(40),
    member_id   bigint,
    guild_id    bigint,
    date        timestamp default current_timestamp,
    in_progress boolean default 1, 

    primary key (id),

    foreign key (dino_name) references DINO(name)               on delete cascade,
    foreign key (member_id) references JUR_PROFILE(member_id)   on delete cascade
);


create table DINO_SEEING(
    id          bigint auto_increment,
    member_id   bigint,
    guild_id    bigint,
    dino_name   varchar(40),
    date        timestamp default current_timestamp,

    primary key (id),

    foreign key (dino_name) references DINO(name)               on delete cascade,
    foreign key (member_id) references JUR_PROFILE(member_id)   on delete cascade

);


create table DISCOVERY_ASSIST(
    id              bigint auto_increment,
    discovery_id    bigint,
    member_id       bigint,
    guild_id        bigint,

    primary key (id),

    foreign key (discovery_id)  references DISCOVERY(id)            on delete cascade,
    foreign key (member_id)     references JUR_PROFILE(member_id)   on delete cascade

);

insert into JUR_SETTINGS values(50,25,10,1.25);
insert into DINO values("diplodocus","link_pl","link_en","path");
insert into JUR_PROFILE(member_id,guild_id) values(123243253454359104,5739264067419520454);
insert into DISCOVERY(dino_name,member_id,guild_id) values("diplodocus",123243253454359104,5739264067419520454);

drop procedure if exists complete_discovery;

delimiter //

create procedure complete_discovery (dn varchar(40), mi bigint)
    begin
        update DISCOVERY
            set in_progress = 0
        where dino_name = dn and member_id = mi;
    end //

delimiter ;




