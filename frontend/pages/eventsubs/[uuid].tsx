import {Paper} from "@mui/material";
import {useRouter} from "next/router";

export default function EventsubPage() {
    const router = useRouter();

    return (<Paper>
        <p>{router.query.uuid}</p>
    </Paper>);
}