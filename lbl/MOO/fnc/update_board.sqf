params ["_unit", "_score"];
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
diag_log ["MOO", MOO_mission_start_system_time, "UPDATED_SCORE_BOARD_IS:" MOO_score_board];
