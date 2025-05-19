addMissionEventHandler ["OnUserSelectedPlayer", {
		params ["_networkId", "_playerObject", "_attempts"];
		[3, _playerObject] spawn MOO_fnc_register_player_handler;
}];