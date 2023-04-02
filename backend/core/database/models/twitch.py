import datetime
from pydantic import BaseModel
from sqlmodel import Field, SQLModel, Column, String

from core.database.models import ObjectMixin


class TwitchEvent(BaseModel):
    broadcaster_user_id: str
    broadcaster_user_login: str
    broadcaster_user_name: str


class ChannelBanEvent(TwitchEvent):
    user_id: str
    user_login: str
    user_name: str
    moderator_user_id: str
    moderator_user_login: str
    moderator_user_name: str
    reason: str
    banned_at: str
    ends_at: str | None
    is_permanent: bool


class ChannelSubscribeEvent(TwitchEvent):
    user_id: str
    user_login: str
    user_name: str
    tier: str
    is_gift: str


class ChannelCheerEvent(TwitchEvent):
    is_anonymous: bool
    user_id: str | None
    user_login: str | None
    user_name: str | None
    message: str
    bits: int


class ChannelUpdateEvent(TwitchEvent):
    title: str
    language: str
    category_id: str
    category_name: str
    is_mature: bool


class ChannelUnbanEvent(TwitchEvent):
    user_id: str
    user_login: str
    user_name: str
    moderator_user_id: str
    moderator_user_login: str
    moderator_user_name: str


class ChannelFollowEvent(TwitchEvent):
    user_id: str
    user_login: str
    user_name: str
    followed_at: datetime.datetime


class ChannelRaidEvent(BaseModel):
    from_broadcaster_user_id: str
    from_broadcaster_user_login: str
    from_broadcaster_user_name: str
    to_broadcaster_user_id: str
    to_broadcaster_user_login: str
    to_broadcaster_user_name: str


class ChannelModeratorAddEvent(TwitchEvent):
    user_id: str
    user_login: str
    user_name: str


class ChannelModeratorRemoveEvent(TwitchEvent):
    user_id: str
    user_login: str
    user_name: str


class TwitchChoice(BaseModel):
    id: str
    title: str
    bits_votes: int
    channel_points_votes: int
    votes: int


class TwitchBitsVoting(BaseModel):
    is_enabled: bool = False
    amount_per_vote: int = 0


class TwitchChannelPointsVoting(BaseModel):
    is_enabled: bool
    amount_per_vote: int


class ChannelPollBeginEvent(TwitchEvent):
    id: str
    title: str
    choices: list[TwitchChoice]
    bits_voting: TwitchBitsVoting
    channel_points_voting: TwitchChannelPointsVoting
    started_at: datetime.datetime
    ends_at: datetime.datetime


class ChannelPollProgressEvent(TwitchEvent):
    id: str
    title: str
    choices: list[TwitchChoice]
    bits_voting: TwitchBitsVoting
    channel_points_voting: TwitchChannelPointsVoting
    started_at: datetime.datetime
    ends_at: datetime.datetime


class ChannelPollEndEvent(TwitchEvent):
    id: str
    title: str
    choices: list[TwitchChoice]
    bits_voting: TwitchBitsVoting
    channel_points_voting: TwitchChannelPointsVoting
    status: str
    started_at: datetime.datetime
    ends_at: datetime.datetime


class TwitchMaxStream(BaseModel):
    is_enabled: bool
    value: int


class TwitchImage(BaseModel):
    url_1x: str
    url_2x: str
    url_4x: str


class TwitchGlobalCooldown(BaseModel):
    is_enabled: bool
    seconds: int


class ChannelPointsCustomRewardAddEvent(TwitchEvent):
    id: str
    is_enabled: bool
    is_paused: bool
    is_in_stock: bool
    title: str
    cost: int
    prompt: str
    is_user_input_required: bool
    should_redemptions_skip_request_queue: bool
    max_per_stream: TwitchMaxStream
    max_per_user_per_stream: TwitchMaxStream
    background_color: str
    image: TwitchImage | None
    default_image: TwitchImage
    global_cooldown: TwitchGlobalCooldown
    cooldown_expires_at: str
    redemptions_redeemed_current_stream: int


class ChannelPointsCustomRewardUpdateEvent(ChannelPointsCustomRewardAddEvent):
    pass


class ChannelPointsCustomRewardRemoveEvent(ChannelPointsCustomRewardAddEvent):
    pass


class TwitchReward(BaseModel):
    id: str
    title: str
    cost: int
    prompt: str


class ChannelPointsCustomRewardRedemptionAddEvent(TwitchEvent):
    id: str
    user_id: str
    user_login: str
    user_name: str
    user_input: str
    status: str
    reward: TwitchReward
    redeemed_at: datetime.datetime


class ChannelPointsCustomRewardRedemptionUpdateEvent(TwitchEvent):
    pass


class TwitchPredictor(BaseModel):
    user_id: str
    user_login: str
    user_name: str
    channel_points_won: int | None
    channel_points_used: int


class TwitchOutcome(BaseModel):
    id: str
    title: str
    color: str
    users: int
    channel_points: int
    top_predictors: list[TwitchPredictor]


class ChannelPredictionBeginEvent(TwitchEvent):
    id: str
    title: str
    outcomes: list[TwitchOutcome]
    started_at: datetime.datetime
    locks_at: datetime.datetime


class ChannelPredictionProgressEvent(ChannelPredictionBeginEvent):
    pass


class ChannelPredictionLockEvent(ChannelPredictionBeginEvent):
    pass


class ChannelPredictionEndEvent(ChannelPredictionBeginEvent):
    winning_outcome_id: str
    status: str


class ChannelSubscriptionEndEvent(ChannelSubscribeEvent):
    pass


class ChannelSubscriptionGiftEvent(TwitchEvent):
    user_id: str
    user_login: str
    user_name: str
    total: int
    tier: str
    cumulative_total: int
    is_anonymous: bool


class TwitchEmote(BaseModel):
    begin: int
    end: int
    id: str


class TwitchMessage(BaseModel):
    text: str
    emotes: list[TwitchEmote]


class ChannelSubscriptionMessageEvent(TwitchEvent):
    user_id: str
    user_login: str
    user_name: str
    tier: str
    message: TwitchMessage
    cumulative_months: int
    streak_months: int
    duration_months: int


class TwitchCharityDonate(BaseModel):
    value: int
    decimal_places: int
    currency: str


class CharityDonationEvent(TwitchEvent):
    id: str
    campaign_id: str
    user_id: str
    user_login: str
    user_name: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    amount: TwitchCharityDonate


class CharityDonationStartEvent(TwitchEvent):
    id: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: TwitchCharityDonate
    target_amount: TwitchCharityDonate
    started_at: datetime.datetime


class CharityDonationProgressEvent(TwitchEvent):
    id: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: TwitchCharityDonate
    target_amount: TwitchCharityDonate


class CharityDonationStopEvent(TwitchEvent):
    id: str
    charity_name: str
    charity_description: str
    charity_logo: str
    charity_website: str
    current_amount: TwitchCharityDonate
    target_amount: TwitchCharityDonate
    stopped_at: datetime.datetime


class TwitchEntitlementData(BaseModel):
    organization_id: str
    category_id: str
    category_name: str
    campaign_id: str
    user_id: str
    user_name: str
    user_login: str
    entitlement_id: str
    benefit_id: str
    created_at: datetime.datetime


class DropEntitlementGrantEvent(BaseModel):
    id: str
    data: list[TwitchEntitlementData]


class TwitchProduct(BaseModel):
    name: str
    bits: int
    sku: str
    in_development: bool


class ExtensionBitsTransactionCreateEvent(TwitchEvent):
    extension_client_id: str
    id: str
    user_id: str
    user_login: str
    user_name: str
    product: TwitchProduct


class GoalsEvent(TwitchEvent):
    id: str
    type: str
    description: str
    is_achieved: bool
    current_amount: int
    target_amount: int
    started_at: datetime.datetime
    ended_at: datetime.datetime


class TwitchContributions(BaseModel):
    user_id: str
    user_login: str
    user_name: str
    type: str
    total: int


class HypeTrainBeginEvent(TwitchEvent):
    id: str
    total: int
    progress: int
    goal: int
    top_contributions: TwitchContributions
    last_contribution: TwitchContributions
    level: int
    started_at: datetime.datetime
    expires_at: datetime.datetime


class HypeTrainProgressEvent(HypeTrainBeginEvent):
    pass


class HypeTrainEndEvent(TwitchEvent):
    id: str
    level: int
    total: int
    top_contributions: TwitchContributions
    started_at: datetime.datetime
    ended_at: datetime.datetime
    cooldown_ends_at: datetime.datetime


class ShieldModeBeginEvent(TwitchEvent):
    moderator_user_id: str
    moderator_user_name: str
    moderator_user_login: str
    started_at: datetime.datetime


class ShieldModeEndEvent(TwitchEvent):
    moderator_user_id: str
    moderator_user_name: str
    moderator_user_login: str
    ended_at: datetime.datetime


class ShoutoutSendEvent(TwitchEvent):
    moderator_user_id: str
    moderator_user_name: str
    moderator_user_login: str
    to_broadcaster_user_id: str
    to_broadcaster_user_name: str
    to_broadcaster_user_login: str
    started_at: datetime.datetime
    viewer_count: int
    cooldown_ends_at: datetime.datetime
    target_cooldown_ends_at: datetime.datetime


class ShoutoutReceiveEvent(TwitchEvent):
    from_broadcaster_user_id: str
    from_broadcaster_user_name: str
    from_broadcaster_user_login: str
    viewer_count: int
    started_at: datetime.datetime


class StreamOnlineEvent(TwitchEvent):
    id: str
    type: str
    started_at: datetime.datetime


class StreamOfflineEvent(TwitchEvent):
    pass


class UserAuthorizationGrantEvent(BaseModel):
    client_id: str
    user_id: str
    user_login: str
    user_name: str


class UserAuthorizationRevokeEvent(UserAuthorizationGrantEvent):
    pass


class UserUpdateEvent(BaseModel):
    user_id: str
    user_login: str
    user_name: str
    email: str | None
    email_verified: bool | None
    description: str


def get_model_by_subscription_type(subscription_type: str, data: dict) -> BaseModel:

    model = BaseModel

    match subscription_type:
        case "channel.update":
            model = ChannelUpdateEvent
        case "channel.follow":
            model = ChannelFollowEvent
        case "channel.subscribe":
            model = ChannelSubscribeEvent
        case "channel.subscription.end":
            model = ChannelSubscriptionEndEvent
        case "channel.subscription.gift":
            model = ChannelSubscriptionGiftEvent
        case "channel.subscription.message":
            model = ChannelSubscriptionMessageEvent
        case "channel.cheer":
            model = ChannelCheerEvent
        case "channel.raid":
            model = ChannelRaidEvent
        case "channel.ban":
            model = ChannelBanEvent
        case "channel.unban":
            model = ChannelUnbanEvent
        case "channel.moderator.add":
            model = ChannelModeratorAddEvent
        case "channel.moderator.remove":
            model = ChannelModeratorRemoveEvent
        case "channel.channel_points_custom_reward.add":
            model = ChannelPointsCustomRewardAddEvent
        case "channel.channel_points_custom_reward.update":
            model = ChannelPointsCustomRewardUpdateEvent
        case "channel.channel_points_custom_reward.remove":
            model = ChannelPointsCustomRewardRemoveEvent
        case "channel.channel_points_custom_reward_redemption.add":
            model = ChannelPointsCustomRewardRedemptionAddEvent
        case "channel.channel_points_custom_reward_redemption.update":
            model = ChannelPointsCustomRewardRedemptionUpdateEvent
        case "channel.poll.begin":
            model = ChannelPollBeginEvent
        case "channel.poll.progress":
            model = ChannelPollProgressEvent
        case "channel.poll.end":
            model = ChannelPollEndEvent
        case "channel.prediction.begin":
            model = ChannelPredictionBeginEvent
        case "channel.prediction.progress":
            model = ChannelPredictionProgressEvent
        case "channel.prediction.lock":
            model = ChannelPredictionLockEvent
        case "channel.prediction.end":
            model = ChannelPredictionEndEvent
        case "channel.charity_campaign.donate":
            model = CharityDonationEvent
        case "channel.charity_campaign.start":
            model = CharityDonationStartEvent
        case "channel.charity_campaign.progress":
            model = CharityDonationProgressEvent
        case "channel.charity_campaign.stop":
            model = CharityDonationStopEvent
        case "drop.entitlement.grant":
            model = DropEntitlementGrantEvent
        case "extension.bits_transaction.create":
            model = ExtensionBitsTransactionCreateEvent
        case "channel.goal.begin":
            model = GoalsEvent
        case "channel.goal.progress":
            model = GoalsEvent
        case "channel.goal.end":
            model = GoalsEvent
        case "channel.hype_train.begin":
            model = HypeTrainBeginEvent
        case "channel.hype_train.progress":
            model = HypeTrainProgressEvent
        case "channel.hype_train.end":
            model = HypeTrainEndEvent
        case "channel.shield_mode.begin":
            model = ShieldModeBeginEvent
        case "channel.shield_mode.end":
            model = ShieldModeEndEvent
        case "channel.shoutout.create":
            model = ShoutoutSendEvent
        case "channel.shoutout.receive":
            model = ShoutoutReceiveEvent
        case "stream.online":
            model = StreamOnlineEvent
        case "stream.offline":
            model = StreamOfflineEvent
        case "user.authorization.grant":
            model = UserAuthorizationGrantEvent
        case "user.authorization.revoke":
            model = UserAuthorizationRevokeEvent
        case "user.update":
            model = UserUpdateEvent

    return model(**data)


class TwitchMessageId(SQLModel, ObjectMixin, table=True):
    message_id: str = Field()
