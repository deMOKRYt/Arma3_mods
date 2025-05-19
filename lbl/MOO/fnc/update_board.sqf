params ["_unit", "_score"];
try
{
	_player_id = getPlayerID _unit;
	_user_info = getUserInfo _player_id;
	_name = _user_info select 4;
	if (_name in MOO_score_board) then {
		_old_score = MOO_score_board get _name;
		_new_score = _old_score + _score;
		MOO_score_board set [_name, _new_score];
	} else {
		MOO_score_board set [_name, _score];
	};
	diag_log ["MOO", MOO_mission_start_system_time, "UPDATED_SCORE_BOARD_IS:", MOO_score_board];
}
catch
{
	// Added this try catch to make sure players are not going to 
	// get anoing errors during gameplay. 
	//
	// In testing I got error when kiling curently controled unit alongside 
	// few AI controled unit with own granade. Most likely unit i was being 
	// transfered to also died in almost same moment. Therfore getUserInfo or 
	// gePlayerId returned nothing.
	
	diag_log ["MOO", "update board failed", "[_unit, _score, _player_id, _user_info]", [_unit, _score, _player_id, _user_info]];
}