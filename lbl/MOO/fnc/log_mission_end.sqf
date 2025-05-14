addMissionEventHandler ["MPEnded", {
	diag_log ["MOO", MOO_mission_start_system_time, "SCORE_BOARD_AFTER_MISSION_END_IS:", MOO_score_board];
	diag_log ["MOO", MOO_mission_start_system_time, "MPEnded"];
}];
