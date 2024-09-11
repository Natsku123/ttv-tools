'use client'
import '@/styles/globals.css'
import React from "react";
import {
    AppBar,
    Box,
    CssBaseline,
    Toolbar,
    Container, Grid, Typography, Divider, ListItemText, List, ListItem, ListItemButton, IconButton, Button, Drawer
} from "@mui/material";
import MenuIcon from '@mui/icons-material/Menu';
import Link from "next/link";
import Footer from "@/src/components/Footer";
import {UserBar} from "@/src/components/UserBar";
import Providers from "@/app/providers";

export default function RootLayout({children}: {
    children: React.ReactNode
}) {
    const [mobileOpen, setMobileOpen] = React.useState(false);

    const handleDrawerToggle = () => {
        setMobileOpen((prevState) => !prevState);
    };

    const drawerWidth = 240;

    const drawer = (
        <Box onClick={handleDrawerToggle} sx={{textAlign: 'center'}}>
            <Typography variant="h6" sx={{my: 2}} component="a"
                        href="/">
                TTV Tools
            </Typography>
            <Divider/>
            <List>
                <ListItem disablePadding>
                    <List>
                        <ListItem disablePadding>
                            <Link href={"/eventsubs"} passHref>
                                <ListItemButton sx={{textAlign: 'center'}}>
                                    <ListItemText primary={"Events"}/>
                                </ListItemButton>
                            </Link>
                        </ListItem>
                    </List>
                </ListItem>
                <ListItem disablePadding>
                    <Link href={`/user/`} passHref>
                        <ListItemButton sx={{textAlign: 'center'}}>
                        </ListItemButton>
                    </Link>
                </ListItem>
            </List>
        </Box>
    );

    return (
        <html lang="en">
        <body>
        <Providers>
            <CssBaseline/>
            <AppBar position="static">
                <Container maxWidth="xl">
                    <Toolbar disableGutters>
                        <Grid container justifyContent={"space-between"}>
                            <Grid item xs container spacing={2}>
                                <Grid item>
                                    <IconButton
                                        color="inherit"
                                        aria-label="open drawer"
                                        edge="start"
                                        onClick={handleDrawerToggle}
                                        sx={{mr: 2, display: {sm: 'none'}}}
                                    >
                                        <MenuIcon/>
                                    </IconButton>
                                    <Link href={'/'} passHref>
                                        <Typography
                                            variant="h6"
                                            noWrap
                                            sx={{flexGrow: 1}}
                                        >
                                            TTV Tools
                                        </Typography>
                                    </Link>
                                </Grid>
                                <Grid item xs>
                                    <Link href={"/eventsubs"} passHref>
                                        <Button sx={{color: 'white', display: {xs: 'none', sm: 'block'}}}>
                                            Events
                                        </Button>
                                    </Link>
                                </Grid>
                            </Grid>
                            <Grid item>
                                <UserBar/>
                            </Grid>
                        </Grid>

                    </Toolbar>
                </Container>
            </AppBar>
            <nav>
                <Drawer
                    variant="temporary"
                    open={mobileOpen}
                    onClose={handleDrawerToggle}
                    ModalProps={{
                        keepMounted: true, // Better open performance on mobile.
                    }}
                    sx={{
                        display: {xs: 'block', sm: 'none'},
                        '& .MuiDrawer-paper': {boxSizing: 'border-box', width: drawerWidth},
                    }}
                >
                    {drawer}
                </Drawer>
            </nav>
            <main>
                <Container>
                    <Box py={2}>
                        {children}
                    </Box>
                </Container>
            </main>
            <footer>
                <Footer/>
            </footer>
        </Providers>
        </body>
        </html>
    )
}
