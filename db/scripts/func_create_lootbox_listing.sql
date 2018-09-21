create function create_lootbox_listing() returns trigger as
$BODY$
begin	
	insert into lootbox_items values (new.id, -1, 0, 100);
	return new;
end;
$BODY$
language plpgsql volatile;