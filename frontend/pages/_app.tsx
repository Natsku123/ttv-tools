import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import {QueryClient} from "@tanstack/query-core";
import React, {useState} from "react";
import {Hydrate, QueryClientProvider} from "@tanstack/react-query";
import {
  AppBar,
  Box,
  CssBaseline,
  ThemeProvider,
  Toolbar,
  Container, Grid, Typography, Divider, ListItemText, List, ListItem, ListItemButton, IconButton, Button, Drawer
} from "@mui/material";
import MenuIcon from '@mui/icons-material/Menu';
import Link from "next/link";
import {theme} from "@/components/theme";
import Footer from "@/components/Footer";
import {UserBar} from "@/components/UserBar";


export default function App({ Component, pageProps }: AppProps) {
  const [queryClient] = useState(() => new QueryClient());

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
                <UserBar />
              </ListItemButton>
            </Link>
          </ListItem>
        </List>
      </Box>
  );

  return (
      <QueryClientProvider client={queryClient}>
        <Hydrate state={pageProps.dehydratedState}>
          <ThemeProvider theme={theme}>
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
                        <Link href={'/'}>
                          <Typography
                              variant="h6"
                              noWrap
                              component="a"
                              href="/"
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
                  <Component {...pageProps} />
                </Box>
              </Container>
            </main>
            <footer>
              <Footer/>
            </footer>
          </ThemeProvider>
        </Hydrate>
      </QueryClientProvider>
  )
}
