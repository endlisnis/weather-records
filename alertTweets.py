import random
from dialog import Dialog
import delayedTweets

# @ChrisScottWx, @DFLCMartins, @MikeGArsenault, @SuzanneTWN: Nothing!
# @bradrousseau: retweeted one of vernon's tweets, but then nothing else.
# @jwhittalTWN: retweeted 3 tweets, but nobody seemed to care
# All the TWN guys ('@cstclair1', '@KMacTWN', '@MeiDayTWN', '@MurphTWN') would do some stuff, but it didn't get me followers

nationalAccounts = ('', '@environmentca')

accountsPerCity = {
    # @CalgaryConnect retweeted 1 time
    # @CBCEyeopener followed on 2015-11-04
    'calgary': ('#YycWx',
                '@cityofcalgary',
                '@CBCCalgary',
                '@nenshi',
                "@calgary",
                "@calgaryherald",
                "@metrocalgary",
                "@CTVCalgary",
                "@calgarytransit",
                "@downtowncalgary",
                "@TourismCalgary",
                "@AvenueMagazine",
                "@GlobalCalgary",
                "@660NEWS",
                "@UCalgary",
                "@calgarystampede",
                "@calgarysun",
                "@CIAwesome",
                "@CalgaryConnect",
                "@SwerveCalgary",
                "@CalgaryCulture",
                "@wherecalgary",
                "@yycfoodtrucks",
                "@CalgaryChamber",
                '@YYCREGuy',
                "@AstridKuhn",
                '@paul_dunphy',
                '@IAmJodiHughes',
                '@CMoleCalgary',
                '@AngelaKnightCBC',
                '@lyndeefree',
                '@CBCDanielle',
            ),

    'charlottetown': ('#PEI',
                      '#PEI411',
    ),
    # @Official_WEM ignored 1 tweet 2015-09-03
    #'@CityofEdmonton',
    #'@edmontonjournal',
    #'@CBCEdmonton',
    #'@GlobalEdmonton',
    #'@metroedmonton',
    #'@Edmontonsun',
    #'@AvenueEdmonton',
    #'@ctvedmonton',
    #'@edmontonstories',
    #'@CitytvEdmonton',
    #'@iheartedmonton',
    #'@VirginRadioYEG',
    #'@Edm_Examiner',
    #'@whereedmonton',
    #'@EdmontonTourism',
    #'@Paulatics',
    #'@HOT107Edmonton',
    #'@mastermaq',
    #'@environmentca'),
    'edmonton': ('#yegwx',
                 '@GarretteMcGowan',
                 '@mikesobel',
                 '@kevinoweather',
                 '@CMoleEdmonton',
                 '@Slummer90',
             ),
    'fredericton': ('#NBStorm',),
    # @NatashaPace followed halifax
    # @RebeccaLau favourited (2015-08-23)
    # @alythomson retweeted (2015-08-24)
    # @hillarywindsor favourited 2 tweets (2015-08-24)
    # @globalalexh followed halifax (2015-10-02)
    # @sdpuddicombe followed halifax (2016-01-31)
    # @SandySmithCBC followed halifax (2016-02-09)
    'halifax': ('#NSWx',
                '@Mainstreethfx',
                '@BrynnELangille',
                '@PeterCoade',
                '@metrohalifax',
                '@alythomson',
                '@larochecbc',
                '@CBCBlairRhodes',
                '',
                '@CBCNS',
                '#NsStorm',
            ),
    'hamilton': ( '#OnStorm', ),
    # @DeniseCTV followed me
    # @jilltaylor680 followed me, and then UN-followed me, now only favorites things.
    # @ellefabbro: nothing
    # @680News: nothing
    # @EmilyTWN: favourited 2015-09-07
    # @gtaweather1: followed on 2015-11-06
    # @CP24: nothing
    'toronto': ('#TOWx',
                '@CBCToronto',
                '@globalnewsto',
                '@CTVToronto',
                '#CityofTO',
                '@TorontoComms',
                '@DanaCTV',
                '@TorontoStar',
                '@Toronto_CP',
                '@AnthonyFarnell',
                '@ellefabbro',
                '#OnStorm'),
    'thunderBay': ('#TBay', '#TBWthr', '@thewalleye', '#OnStorm', '@MaryJeanCBC'),
    # @AnthonyFarnell retweeted 2 montreal tweets
    # @CBCMontreal favourited 1 tweet (2015-08-15)
    # @Global_Montreal rewteeted 1 montreal tweet: 20015-09-08
    'montreal': (
        '@AnthonyFarnell',
        '@BTMontreal',
        '@CBCMontreal',
        '@CJAD800',
        '@CTVMontreal',
        '@Global_Montreal',
        '@JessLaventure',
        '@cbcdaybreak',
        '@MHarroldCTV',
        '#QcStorm',
    ),
    'quebec': ('#QcStorm', ),


    # @KMacTWN followed ottawa
    # @NicoleKarkic favourited ottawa
    # @OttawaAthletic liked 2015-09-07
    # @ottawa_events ignored everything
    # @mec_ottawa ignored everything
    # @RobynBresnahan ignored everything
    # @cmaconthehill ignored everything
    # @ottawa_tweetup ignored everything
    # @whereottawa ignored everything
    # @OttawaDailyNews ignored everything
    # @GeorgeDarouze (City councillor) liked 2016-02-07
    # @cathmckenna followed 2015-12-10
    #'@MathieuFleury', #City councillor
    #'@JLeiper', #City councillor
    #'@RiverWardRiley', #City councillor
    #'@JeanCloutierOtt', #City councillor
    #'@tobi_nussbaum', #City councillor
    #'@RickChiarelli',
    #'@QaqishPolitico', #City councillor
    #'@AllanHubley_23', #City councillor
    #'@BobMonette1', #City councillor
    #'@Eli_ElChantiry', #City councillor
    #'@ShadQadri', #City councillor
    #'@dianedeans', #City councillor
    #'@chernushenko', #City councillor
    #'@marianne4kanata', #City councillor
    #'@BarrhavenJan', #City councillor
    #'@ScottMoffatt21', #City councillor
    #'@Go_Taylor', #City councillor
    #'@JODYMITIC', #City councillor
    #'@StephenBlais', #City councillor
    #'@cmckenney', #City councillor
    #'@TimTierney', #City councillor
    # @CTVOttMornLive
    'ottawa': ('',
               '@NCC_Skateway',
               '@slunney',
               '@BlacksWeather',
               '@MaOnTheAir',
               '@cwadsworthCTV',
               '@StuntmanStu',
               '@newcountry94',
               '@meghan_hurley',
               '#OttWeather',
               '#OttWx',
               '#OttNews',
               '#OnStorm'),
    'regina': ('@ChristyCBC', '@CTVKahla', '@JCGardenCTV', '@LizPGlobal'),
    # @MurphTWN followed stjohns
    # @ryansnoddon followed stjohns on 2015-11-09
    # @kellymbutt followed stjohns
    # @CityofStJohns
    # @StJohnsTelegram
    # @stjohnsairport
    # @TelegramJames
    # @DowntownStJohns
    # @StJohnsEOC
    # @StJohnsPrideNL
    # @DanMacEachern
    'stjohns':  ('@EddieSheerr',
                 '#NLWx',
             ),

    'waterloo': ('#OnStorm',),
    'winnipeg': ('@johnsauderCBC',
                 '@ColleenCTV',
                 '@MichelleLissel',
                 '@MikeKoncan'),
    # @CBCVancouver
    'vancouver': ('#YvrWx', '@JWagstaffe', '@50ShadesofVan'),
    'vernon': ('@VernonNews',
               '@TourismVernon',
               '@CityofVernon',
               '@SuttonVernonBC',
               '@BlenzVernonBC',
               '@bikramvernon',
               '@HabitatVernon',
               '@VernonNightOut',
               '@VernonBCNews',
               '@wilfmulder',
               '@GlobalOkanagan',
           ),
}

accountsPerCity['edmonton-airport'] = accountsPerCity['edmonton']

def shouldTweetSuffix(city, text, *, accountHint=None, oldText=None):
    fullList = nationalAccounts + accountsPerCity.get(city, tuple())
    choices = []
    for i, a in enumerate(fullList):
        choices.append((str(i), a))

    showText = '{}: {}'.format(len(text), text)
    if oldText is not None:
        showText = 'Old: {}\n{}'.format(oldText, showText)
    code, tag = Dialog().menu(
        text=showText,
        choices=choices,
        height=30, width=50)
    if code=='ok':
        return True, text + ' {account}'.format(account=fullList[int(tag)])
    return False, text

def maybeTweetWithSuffix(city, text, *, accountHint=None, oldText=None, fname=None):
    (use, tweet) = shouldTweetSuffix(city, text, accountHint=accountHint, oldText=oldText)
    if use is True:
        if fname is None:
            delayedTweets.addToEndOfListForCity(city, tweet)
        else:
            delayedTweets.addToEndOfListForCity(city, tweet, fname)
        print("ok")
    return (use, tweet)
