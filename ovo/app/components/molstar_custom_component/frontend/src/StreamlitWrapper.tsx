import {
    StreamlitComponentBase,
    withStreamlitConnection,
    Streamlit
} from "streamlit-component-lib";
import React, { ReactNode } from "react";
import MolstarCustomComponent from "./MolstarCustomComponent";
import { ContigSegment, StreamlitComponentValue } from "./types";

interface State {
    highlightedContig: ContigSegment & { structureIdx: number; } | null;
    currentComponentState: StreamlitComponentValue | null;
    isFullscreen: boolean;
}

// Helper function to ensure color is dark enough on white background
function ensureReadableColor(color: string): string {
    // Parse hex color
    const hex = color.replace('#', '');
    const r = parseInt(hex.substr(0, 2), 16) / 255;
    const g = parseInt(hex.substr(2, 2), 16) / 255;
    const b = parseInt(hex.substr(4, 2), 16) / 255;

    // Calculate relative luminance
    const luminance = (c: number) => c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    const L = 0.2126 * luminance(r) + 0.7152 * luminance(g) + 0.0722 * luminance(b);

    // White has luminance of 1
    // Contrast ratio = (L1 + 0.05) / (L2 + 0.05) where L1 is lighter
    const contrastRatio = (1 + 0.05) / (L + 0.05);

    // WCAG AA recommends 4.5:1 for normal text
    const threshold = 3.5;
    if (contrastRatio < threshold) {
        // Darken the color by reducing RGB values
        const darkenFactor = Math.sqrt(threshold / contrastRatio);
        const newR = Math.floor(r * 255 / darkenFactor);
        const newG = Math.floor(g * 255 / darkenFactor);
        const newB = Math.floor(b * 255 / darkenFactor);
        return `#${newR.toString(16).padStart(2, '0')}${newG.toString(16).padStart(2, '0')}${newB.toString(16).padStart(2, '0')}`;
    }

    return color;
}

class StreamlitWrapper extends StreamlitComponentBase<State> {

    constructor(props: any) {
        super(props);
        this.state = { highlightedContig: null, currentComponentState: null, isFullscreen: false };

        this.setHighlightedContig = this.setHighlightedContig.bind(this);
        this.updateStreamlitComponentValue = this.updateStreamlitComponentValue.bind(this);
        this.handleFullscreenChange = this.handleFullscreenChange.bind(this);
    }

    componentDidMount() {
        document.addEventListener('fullscreenchange', this.handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', this.handleFullscreenChange);

        // Use a small delay to allow the DOM to fully render
        setTimeout(() => {
            Streamlit.setFrameHeight();
        }, 100);
    }

    componentWillUnmount() {
        document.removeEventListener('fullscreenchange', this.handleFullscreenChange);
        document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange);
    }

    handleFullscreenChange = () => {
        const isFullscreen = !!(
            document.fullscreenElement || (document as any).webkitFullscreenElement
        );

        this.setState({ isFullscreen });

        // notify Streamlit to resize after exiting fullscreen
        if (!isFullscreen) {
            setTimeout(() => {
                Streamlit.setFrameHeight();
            }, 100);
        }
    };

    setHighlightedContig = (newContig: ContigSegment, structureIdx: number) => {
        this.setState(prevState => {
            return {
                ...prevState,
                highlightedContig: {
                    ...newContig,
                    structureIdx: structureIdx
                }
            };
        });
    };

    updateStreamlitComponentValue = (newValue: StreamlitComponentValue) => {
        this.setState(prevState => {
            if (prevState?.currentComponentState) {
                const prevValueString = JSON.stringify(prevState.currentComponentState);
                const newValueString = JSON.stringify(newValue);
                if (prevValueString !== newValueString) {
                    Streamlit.setComponentValue(newValueString);
                }
            }
            return {
                ...prevState,
                currentComponentState: newValue
            };
        });
    };

    public render = (): ReactNode => {
        const structures = JSON.parse(this.props.args["structures"]);
        const key = this.props.args["key"];
        const divName = `molstar-wrapper-${key}`;
        const showControls = this.props.args["showControls"];
        const selectionMode = this.props.args["selectionMode"];
        const forceReload = this.props.args["forceReload"] ?? false;

        const requestedHeight = this.props.args["height"];
        const contigsHeight = 25; // for the contigs

        const originalWidth = this.props.args["width"];
        const effectiveWidth = this.state.isFullscreen ? "100%" : originalWidth;

        // parse all contigs for each of the structures
        const allContigsParsed: ContigSegment[][] = [];
        structures.forEach((s: any) => allContigsParsed.push(s["contigs"] ?? []));

        return (
            <>
                <div id={divName} style={{ height: requestedHeight, width: effectiveWidth }}>
                    <MolstarCustomComponent structures={structures} divName={divName} showControls={showControls}
                        contigs={allContigsParsed} highlightedContig={this.state.highlightedContig}
                        selectionMode={selectionMode} updateStreamlitComponentValue={this.updateStreamlitComponentValue}
                        forceReload={forceReload}
                    />
                </div>
                {!this.state.isFullscreen && allContigsParsed.map((parsedContigs, outerIdx) => {
                    const labeledSegments = parsedContigs.filter((e, idx) => e.middle_label || e.start_label);
                    if (labeledSegments.length > 0) return (
                        <div className="msp-layout-contig" style={{ color: "black", fontSize: "14px", cursor: "default" }} key={outerIdx}>
                            Segments: {labeledSegments.map((e, idx) => {
                                const contigDescription = e.middle_label ? `${e.middle_label} ` : `${e.start_label}-${e.end_label} `;
                                return <span style={{ color: ensureReadableColor(e.color) }} onMouseOver={() => this.setHighlightedContig(e, outerIdx)} key={idx}>{contigDescription}</span>;
                            })}
                        </div>);
                    return <React.Fragment key={outerIdx}></React.Fragment>;
                })}
            </>
        );
    };
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
export default withStreamlitConnection(StreamlitWrapper);
