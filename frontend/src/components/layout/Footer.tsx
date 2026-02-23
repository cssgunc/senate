import Link from "next/link";

export function Footer() {
    return (
        <footer className="w-full border-t bg-background py-12">
            <div className="container mx-auto px-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
                    {/* Contact Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-primary">Contact Us</h3>
                        <div className="text-sm text-muted-foreground space-y-2">
                            <p>UNC Student Government - Upper Chamber</p>
                            <p>Student Union, Suite 3109</p>
                            <p>Chapel Hill, NC 27599</p>
                            <p>Email: <a href="mailto:senate@unc.edu" className="hover:text-primary underline-offset-4 hover:underline">senate@unc.edu</a></p>
                        </div>
                    </div>

                    {/* Student Government Resources */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-primary">Student Government</h3>
                        <ul className="text-sm space-y-2 text-muted-foreground">
                            <li>
                                <a href="https://studentgovernment.unc.edu/" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">
                                    Undergraduate Student Government
                                </a>
                            </li>
                            <li>
                                <a href="https://executivebranch.unc.edu/" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">
                                    Executive Branch
                                </a>
                            </li>
                            <li>
                                <a href="https://studentgovernment.unc.edu/jgc/" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">
                                    Joint Governance Council (JGC)
                                </a>
                            </li>
                        </ul>
                    </div>

                    {/* Other Branches Section */}
                    <div className="space-y-4">
                        <h3 className="text-lg font-semibold text-primary">Other Branches</h3>
                        <ul className="text-sm space-y-2 text-muted-foreground">
                            <li>
                                <a href="https://gpsg.unc.edu/" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">
                                    GPSG (Graduate & Professional)
                                </a>
                            </li>
                            <li>
                                <a href="https://studentsupremecourt.unc.edu/" target="_blank" rel="noopener noreferrer" className="hover:text-primary transition-colors">
                                    Student Supreme Court
                                </a>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Bottom Bar */}
                <div className="mt-12 pt-8 border-t text-center text-sm text-muted-foreground">
                    <p>&copy; {new Date().getFullYear()} Undergraduate Student Government - Undergraduate Senate at UNC Chapel Hill.</p>
                </div>
            </div>
        </footer>
    );
}
