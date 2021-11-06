// declare include paths
#include "path://media/packages/vanilla/scripts"
#include "path://media/packages/varvaytya_test/scripts"

#include "gamemode_invasion.as"

// --------------------------------------------
void main(dictionary@ inputData) {
    _setupLog("dev_verbose");
    XmlElement inputSettings(inputData);
    _log("debug: inputSettings = ");
    _log(inputSettings.toStringWithFloats());
    UserSettings settings;
    // HACK: [] set the username from the local inputData as this main begins at campaign entry script
    string username = "";
    if (!inputData.get("username", username)) {
        _log("username key not in inputData dict");
    }
    settings.m_username = username;
    settings.m_factionChoice = 0;                   // 0 (greenbelts), 1 (graycollars), 2 (brownpants)
    settings.m_playerAiCompensationFactor = 1.0;
    settings.m_enemyAiAccuracyFactor = 0.95;
    settings.m_playerAiReduction = 0.0;             // didn't work before 1.76! (was 1.0)
    settings.m_teamKillPenaltyEnabled = false;      // HACK: mod for  tester invasion
    settings.m_completionVarianceEnabled = false;
    settings.m_journalEnabled = false;              // HACK: mod for  tester invasion
    settings.m_fellowDisableEnemySpawnpointsSoldierCountOffset = 1;
    // HACK: [] some of these  things require XP and RP, improve reward factor and starting amounts
    settings.m_xpFactor = 5.0;
    /* settings.m_rpFactor = 1.0; */
    settings.m_initialXp = 100.0;
    settings.m_initialRp = 1000000.0;
    // HACK: [] when there aren't enough enemies around, test these weapons on your allies instead XD
    settings.m_friendlyFire = true;
    // HACK: [] enable testing tools!
    settings.m_testingToolsEnabled = true;


    array<string> overlays = { "media/packages/invasion", "media/packages/_varvaytya_test_pkg" };
    settings.m_overlayPaths = overlays;

    // HACK: [] don't automatically start a server for  testing
    settings.m_startServerCommand = """
<command class='start_server'
    server_name='incursion varvaytya test'
    server_port='1240'
    profile_server_url='127.0.0.1:5000/'
    realm='INCURSION'
    realm_secret='ilmoittautua'
    realm_password='test12345'
    comment='Coop campaign'
    url=''
    register_in_serverlist='1'
    mode='COOP'
    persistency='forever'
    max_players='8'>
    <client_faction id='0' />
</command>
""";

    settings.print();
    GameModeInvasion metagame(settings);
    metagame.init();
    // HACK: [] add local player as admin for easy testing, hacks, etc
    if (!metagame.getAdminManager().isAdmin(metagame.getUserSettings().m_username)) {
        metagame.getAdminManager().addAdmin(metagame.getUserSettings().m_username);
    }


    metagame.run();
    metagame.uninit();

    _log("ending execution");
}
