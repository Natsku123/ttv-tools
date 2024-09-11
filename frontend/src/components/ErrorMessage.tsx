import {Typography} from "@mui/material";

interface ErrorMessageProps {
    code: number | undefined | string;
    message: string;
}

export default function ErrorMessage({ code, message}: ErrorMessageProps) {
    return (
        <>
            {code && <Typography variant={"h3"}>{code}</Typography> }
            <Typography>{message}</Typography>
        </>
    )
}