create trigger lootbox_inserts 
	after insert 
	on lootboxes 
	for each row
	execute procedure create_lootbox_listing();