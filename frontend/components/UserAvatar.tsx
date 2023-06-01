import {Avatar} from "@mui/material";
import {User} from "@/services/types";

interface AvatarSize {
    width: number | undefined;
    height: number | undefined;
}

interface UserAvatarProps {
    user: User;
    sx?: AvatarSize;
}

export default function UserAvatar({ user, sx }: UserAvatarProps) {
    return (
        <>
            { user?.icon_url && user.icon_url != ""
                ? <Avatar alt={user.name} src={user.icon_url} sx={sx}/>
                : <Avatar alt={user.name} sx={sx}>{user.name[0]}</Avatar>
            }
        </>
    )
}