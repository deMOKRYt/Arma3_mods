class MOO
{
	tag = "MOO"; // Functions tag.  Functions will be called as [] call MOO_fnc_whatever

	class initializers
	{
		class init_variables {
			file = "lbl\MOO\fnc\initialValues.sqf";
			description  = "Initialize some variables";
			preInit = 1;
		};
	};
	
	class leader_board_logger_functions
	{
		class log_mission_start {
			file = "lbl\MOO\fnc\log_mission_start.sqf";
			description = "Logs start of a mission.";
			preInit = 1;
		};

		class add_player_to_leader_board_on_connect {
			file = "lbl\MOO\fnc\add_player_to_leader_board_on_connect.sqf";
			description = "Add player to leader board on connect.";
			preInit = 1; 
		};

		class log_mission_end {
			file = "lbl\MOO\fnc\log_mission_end.sqf";
			description = "Logs leader board and end of a started mission.";
			preInit = 1;
		};

		class update_board {
			file = "lbl\MOO\fnc\update_board.sqf";
			description = "Updates board.";
		};

		class register_player_handler {
			file = "lbl\MOO\fnc\register_player_handler.sqf";
			description = "Register EH.";
		};
	};
};