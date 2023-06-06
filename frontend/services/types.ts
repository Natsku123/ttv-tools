interface Base {
    readonly uuid?: string | undefined;
    readonly created_on?: string | undefined;
    readonly updated_on?: string | undefined;
}

interface Team extends Base {
    name: string;
    description: string;
    members?: Array<User> | undefined
}

interface User extends Base{
    readonly discord_id?: string | undefined;
    readonly twitch_id: string;
    readonly name: string;
    readonly login_name?: string | undefined;
    readonly icon_url?: string | undefined;
    readonly offline_image_url?: string | undefined;
    readonly description?: string | undefined;
    is_superadmin: boolean;
    readonly teams?: Array<Team> | undefined;
}

interface DiscordChannel {
    readonly discord_id: string;
    readonly name: string;
    readonly jump_url: string;
}

interface DiscordUser {
    readonly discord_id: string;
    readonly avatar_url: string;
    readonly name: string;
    readonly mention: string;
    readonly is_admin: boolean;
}

interface DiscordServer {
    readonly discord_id: string;
    readonly name: string;
    readonly icon_url: string;
    readonly description: string;
    readonly owner: DiscordUser;
    readonly channels: Array<DiscordChannel>;
}

interface EventSubscription extends Base {
    user_uuid: string;
    server_discord_id: string;
    channel_discord_id: string;
    event: string;
    readonly twitch_id?: string | undefined;
    custom_title?: string | undefined;
    custom_description?: string | undefined;
}

interface TeamInvite extends Base {
    team_uuid: string;
    user_twitch_id: string;
}

interface Membership extends Base {
    team_uuid: string;
    user_uuid: string;
    is_admin: boolean;
    allowed_invites: boolean;
}

export type {
    Team,
    User,
    DiscordServer,
    DiscordChannel,
    DiscordUser,
    Membership,
    TeamInvite,
    EventSubscription
}