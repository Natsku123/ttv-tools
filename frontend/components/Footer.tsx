import {
    Box,
    Container,
    Divider,
    Grid,
    List,
    ListItem,
    ListItemButton, ListItemIcon,
    ListItemText,
    Paper,
    Typography
} from "@mui/material";
import React from "react";
import {GitHub} from "@mui/icons-material";

export default function Footer() {
    return (<Paper>
        <Container maxWidth={"xl"}>
            <Box py={2}>
                <Grid container>
                    <Grid item>
                        <Typography variant={"h4"}>TTV Tools</Typography>
                        <Typography variant={"h6"}>by Natsku</Typography>
                        <Divider/>
                        <List>
                            <ListItem disablePadding>
                                <ListItemButton href={"https://github.com/Natsku123/ttv-tools"}>
                                    <ListItemIcon>
                                        <GitHub />
                                    </ListItemIcon>
                                    <ListItemText primary={"Github"}/>
                                </ListItemButton>
                            </ListItem>
                        </List>
                    </Grid>
                </Grid>
            </Box>
        </Container>
    </Paper>);
}