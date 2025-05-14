addMissionEventHandler ["PlayerConnected", {
	params ["_id", "_uid", "_name", "_jip", "_owner", "_idstr"];
	[2, _uid] spawn MOO_fnc_register_player_handler;
	}];