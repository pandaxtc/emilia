create function create_user_currency() returns trigger as
$BODY$
begin
	insert into user_items values (new.id, 0, 0);
	return new;
end;
$BODY$
language plpgsql volatile;