create trigger user_inserts 
	after insert 
	on users 
	for each row
	execute procedure create_user_currency();