import '@/styles/globals.css'
import type { AppProps } from 'next/app'
import {QueryClient} from "@tanstack/query-core";
import {useState} from "react";
import {Hydrate, QueryClientProvider} from "@tanstack/react-query";
import {
  AppBar,
  Box,
  CssBaseline,
  ThemeProvider,
  Toolbar,
  Link as MaterialLink,
  Container, Grid
} from "@mui/material";
import Link from "next/link";
import {theme} from "@/pages/theme";
import Footer from "@/components/Footer";
import {UserBar} from "@/components/UserBar";


export default function App({ Component, pageProps }: AppProps) {
  const [queryClient] = useState(() => new QueryClient());

  return (
      <QueryClientProvider client={queryClient}>
        <Hydrate state={pageProps.dehydratedState}>
          <ThemeProvider theme={theme}>
            <CssBaseline />
            <AppBar position="static">
              <Toolbar disableGutters>
                <Grid container justifyContent={"space-between"}>
                  <Grid item>
                    <Box px={2}>
                      <Link href={'/'} passHref>
                        <MaterialLink
                            variant="h6"
                            noWrap
                            style={{ textDecoration: 'none', boxShadow: 'none', color: '#ffffff' }}
                            sx={{ mr: 2, display: { xs: 'none', md: 'flex' } }}>
                          TTV Tools
                        </MaterialLink>
                      </Link>
                    </Box>
                  </Grid>
                  <Grid item>
                    <UserBar />
                  </Grid>
                </Grid>
              </Toolbar>
            </AppBar>
            <main>
              <Container>
                <Box py={2}>
                  <Component {...pageProps} />
                </Box>
              </Container>
            </main>
            <footer>
              <Footer />
            </footer>
          </ThemeProvider>
        </Hydrate>
      </QueryClientProvider>
  )
}
