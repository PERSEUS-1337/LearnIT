import { Inter } from "next/font/google";
import "./globals.css";
import Wrapper from "./Wrapper";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
    title: "LearnIt | Empower Learning with AI",
    description: "Learn more effectively with our new powerful tool.",
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <body className={inter.className}>
                <Wrapper>{children}</Wrapper>
            </body>
        </html>
    );
}
