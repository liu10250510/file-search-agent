#!/usr/bin/env python3
"""
File Search Agent - Streamlit Web Interface
A web-based tool for searching files on your local machine
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from pathlib import Path
import logging
from typing import List, Dict, Any
import subprocess
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.searchers import LocalFileSearcher, SearchResult
from src.config import Config

# Configure logging
logging.basicConfig(level=logging.WARNING)

class StreamlitApp:
    """Streamlit web application for the File Search Agent"""
    
    def __init__(self):
        self.config = Config()
        self.search_config = self.config.get_search_config()
        self.output_config = self.config.get_output_config()
        
        # Initialize session state
        if 'search_results' not in st.session_state:
            st.session_state.search_results = []
        if 'search_history' not in st.session_state:
            st.session_state.search_history = []
    
    def run(self):
        """Main application entry point"""
        st.set_page_config(
            page_title="File Search Agent",
            page_icon="🔍",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.title("🔍 File Search Agent")
        st.markdown("A powerful tool for searching files on your local machine")
        
        # Sidebar for configuration
        self._render_sidebar()
        
        # Main content area
        self._render_main_content()
    
    def _render_sidebar(self):
        """Render the sidebar with search options"""
        st.sidebar.header("⚙️ Search Configuration")
        
        # Search type selection
        search_type = st.sidebar.selectbox(
            "Search Type",
            ["Name", "Content", "Size"],
            help="Choose the type of search to perform"
        )
        
        # Common options
        st.sidebar.subheader("🔧 Options")
        
        include_hidden = st.sidebar.checkbox(
            "Include hidden files",
            value=self.search_config.get('include_hidden', False),
            help="Include files and directories starting with '.'"
        )
        
        case_sensitive = st.sidebar.checkbox(
            "Case sensitive",
            value=self.search_config.get('case_sensitive', False),
            help="Perform case-sensitive searches"
        )
        
        max_depth = st.sidebar.number_input(
            "Maximum depth",
            min_value=1,
            max_value=20,
            value=self.search_config.get('max_depth') or 10,
            help="Maximum directory depth to search"
        )
        
        max_results = st.sidebar.number_input(
            "Maximum results",
            min_value=10,
            max_value=1000,
            value=self.output_config.get('max_results', 100),
            help="Maximum number of results to display"
        )
        
        # Advanced options
        with st.sidebar.expander("🔍 Advanced Options"):
            exclude_patterns_text = st.text_area(
                "Exclude patterns (one per line)",
                value="\n".join(self.search_config.get('exclude_patterns', [])),
                help="File patterns to exclude from search",
                key="exclude_patterns_input"
            )
            exclude_patterns = exclude_patterns_text.strip().split('\n') if exclude_patterns_text.strip() else []
            
            exclude_paths_text = st.text_area(
                "Exclude path patterns (one per line)",
                value="\n".join(self.search_config.get('exclude_paths', [])),
                help="Path patterns to exclude (e.g., */build/*, */venv/*, */.git/*)",
                key="exclude_paths_input"
            )
            exclude_paths = exclude_paths_text.strip().split('\n') if exclude_paths_text.strip() else []
            
            # Content search performance settings
            max_file_size_mb = st.number_input(
                "Max file size for content search (MB)",
                min_value=1,
                max_value=100,
                value=10,
                help="Skip files larger than this when searching content (improves performance)"
            )
            
            # Store in session state for access in search
            st.session_state.max_file_size_mb = max_file_size_mb
            
            include_patterns_text = st.text_area(
                "Include patterns (one per line)",
                value="\n".join(self.search_config.get('include_patterns', [])),
                help="File patterns to include in search",
                key="include_patterns_input"
            )
            include_patterns = include_patterns_text.strip().split('\n') if include_patterns_text.strip() else []
        
        # Store configuration in session state
        st.session_state.search_config = {
            'search_type': search_type,
            'include_hidden': include_hidden,
            'case_sensitive': case_sensitive,
            'max_depth': max_depth,
            'max_results': max_results,
            'exclude_patterns': exclude_patterns,
            'exclude_paths': exclude_paths,
            'include_patterns': include_patterns
        }
    
    def _render_main_content(self):
        """Render the main content area"""
        # Search input section
        self._render_search_input()
        
        # Results section
        if st.session_state.search_results:
            self._render_results()
        
        # Search history
        if st.session_state.search_history:
            self._render_search_history()
    
    def _render_search_input(self):
        """Render the search input section"""
        st.header("🔍 Search Files")
        
        config = st.session_state.search_config
        search_type = config['search_type']
        
        col1, col2 = st.columns([3, 1])
        
        # Initialize variables
        pattern = None
        file_patterns = None
        min_size = None
        max_size = None
        
        with col1:
            # Search path
            search_path = st.text_input(
                "Search Path",
                value=str(Path.home()),
                help="Directory path to search in"
            )
            
            if search_type == "Name":
                pattern = st.text_input(
                    "File Name Pattern",
                    placeholder="e.g., *.py, config*, document.txt",
                    help="Use wildcards (*) for pattern matching"
                )
            elif search_type == "Content":
                pattern = st.text_input(
                    "Search Text",
                    placeholder="e.g., function main, TODO, import numpy",
                    help="Text to search for inside files"
                )
                
                file_patterns = st.text_input(
                    "File Types (optional)",
                    placeholder="e.g., *.py, *.txt, *.md",
                    help="Comma-separated list of file patterns to search in"
                )
            else:  # Size search
                st.subheader("📏 File Size Search")
                col_min, col_max = st.columns(2)
                
                with col_min:
                    st.write("**Minimum Size**")
                    min_size_value = st.number_input(
                        "Size value",
                        min_value=0.0,
                        value=0.0,
                        step=1.0,
                        key="min_size_value",
                        label_visibility="collapsed"
                    )
                    min_size_unit = st.selectbox(
                        "Unit",
                        options=["B", "KB", "MB", "GB", "TB"],
                        index=2,  # Default to MB
                        key="min_size_unit",
                        label_visibility="collapsed"
                    )
                    
                    # Create size string and validate
                    if min_size_value > 0:
                        min_size = f"{min_size_value:.0f}{min_size_unit}"
                        try:
                            min_size_bytes = self._parse_size(min_size)
                            st.caption(f"= {self._format_size(min_size_bytes)}")
                        except ValueError as e:
                            st.error(f"Invalid size: {e}")
                            min_size = None
                    else:
                        min_size = None
                
                with col_max:
                    st.write("**Maximum Size**")
                    max_size_value = st.number_input(
                        "Size value",
                        min_value=0.0,
                        value=0.0,
                        step=1.0,
                        key="max_size_value",
                        label_visibility="collapsed"
                    )
                    max_size_unit = st.selectbox(
                        "Unit",
                        options=["B", "KB", "MB", "GB", "TB"],
                        index=3,  # Default to GB
                        key="max_size_unit",
                        label_visibility="collapsed"
                    )
                    
                    # Create size string and validate
                    if max_size_value > 0:
                        max_size = f"{max_size_value:.0f}{max_size_unit}"
                        try:
                            max_size_bytes = self._parse_size(max_size)
                            st.caption(f"= {self._format_size(max_size_bytes)}")
                        except ValueError as e:
                            st.error(f"Invalid size: {e}")
                            max_size = None
                    else:
                        max_size = None
                
                pattern = None  # Not used for size search
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            search_button = st.button(
                "🔍 Search",
                type="primary",
                use_container_width=True
            )
        
        # Perform search
        if search_button:
            if search_type in ["Name", "Content"] and not pattern:
                st.error("Please enter a search pattern")
                return
            
            if search_type == "Size":
                # Check if we have any size criteria
                if min_size is None and max_size is None:
                    st.error("Please specify minimum and/or maximum size")
                    return
            
            self._perform_search(search_type, search_path, pattern, config, 
                               file_patterns,
                               min_size,
                               max_size,
                               st.session_state.get('max_file_size_mb', 10))
    
    def _perform_search(self, search_type: str, search_path: str, pattern: str, 
                       config: Dict, file_patterns: str = None, 
                       min_size: str = None, max_size: str = None,
                       max_file_size_mb: int = 10):
        """Perform the actual search"""
        try:
            # Validate search path to prevent issues
            search_path = os.path.abspath(search_path)
            if not os.path.exists(search_path):
                st.error(f"Search path does not exist: {search_path}")
                return
            
            # Limit max_depth to prevent infinite recursion
            max_depth = min(config['max_depth'], 20)  # Cap at 20 levels
            max_results = min(config['max_results'], 10000)  # Cap at 10k results
            
            # Initialize searcher
            searcher = LocalFileSearcher(
                include_hidden=config['include_hidden'],
                max_depth=max_depth,
                include_patterns=config['include_patterns'],
                exclude_patterns=config['exclude_patterns'],
                exclude_paths=config['exclude_paths']
            )
            
            # Show progress
            with st.spinner(f"Searching files by {search_type.lower()}..."):
                results = []
                processed_count = 0
                max_iterations = 50000  # Safety limit to prevent infinite loops
                
                if search_type == "Name":
                    result_generator = searcher.search_by_name(
                        search_path=search_path,
                        pattern=pattern,
                        case_sensitive=config['case_sensitive']
                    )
                elif search_type == "Content":
                    fp_list = [fp.strip() for fp in file_patterns.split(',')] if file_patterns else None
                    # Convert MB to bytes for the searcher
                    max_file_size_bytes = max_file_size_mb * 1024 * 1024
                    result_generator = searcher.search_by_content(
                        search_path=search_path,
                        pattern=pattern,
                        file_patterns=fp_list,
                        case_sensitive=config['case_sensitive'],
                        max_file_size=max_file_size_bytes
                    )
                else:  # Size
                    min_bytes = self._parse_size(min_size) if min_size else None
                    max_bytes = self._parse_size(max_size) if max_size else None
                    result_generator = searcher.search_by_size(
                        search_path=search_path,
                        min_size=min_bytes,
                        max_size=max_bytes
                    )
                
                # Collect results with safety limits
                for i, result in enumerate(result_generator):
                    processed_count += 1
                    
                    # Multiple safety breaks to prevent infinite loops
                    if i >= max_results:
                        st.warning(f"Reached maximum result limit ({max_results}). Search stopped.")
                        break
                    if processed_count >= max_iterations:
                        st.warning(f"Reached safety iteration limit ({max_iterations}). Search stopped.")
                        break
                    
                    results.append(result)
                
                # Store results and add to history
                st.session_state.search_results = results
                
                # Create appropriate pattern description for history
                if search_type == "Size":
                    pattern_desc = f"min: {min_size or 'none'}, max: {max_size or 'none'}"
                else:
                    pattern_desc = pattern or "no pattern"
                
                st.session_state.search_history.append({
                    'timestamp': datetime.now(),
                    'type': search_type,
                    'pattern': pattern_desc,
                    'path': search_path,
                    'results_count': len(results)
                })
                
                if results:
                    st.success(f"Found {len(results)} files")
                else:
                    st.warning("No files found matching the search criteria")
        
        except Exception as e:
            st.error(f"Search failed: {str(e)}")
    
    def _render_results(self):
        """Render the search results"""
        st.header("📊 Search Results")
        
        results = st.session_state.search_results
        
        # Results summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Files", len(results))
        with col2:
            total_size = sum(r.size for r in results)
            st.metric("Total Size", self._format_size(total_size))
        with col3:
            file_types = len(set(r.file_type for r in results))
            st.metric("File Types", file_types)
        with col4:
            avg_size = total_size / len(results) if results else 0
            st.metric("Average Size", self._format_size(avg_size))
        
        # Visualization tabs
        tab1, tab2, tab3 = st.tabs(["📋 Table View", "📊 Charts", "💾 Export"])
        
        with tab1:
            self._render_results_table(results)
        
        with tab2:
            self._render_results_charts(results)
        
        with tab3:
            self._render_export_options(results)
    
    def _render_results_table(self, results: List[SearchResult]):
        """Render results as a table"""
        if not results:
            st.info("No results to display")
            return
        
        # Convert to DataFrame
        data = []
        for result in results:
            data.append({
                'Name': result.name,
                'Path': result.path,
                'Size': self._format_size(result.size),
                'Size (bytes)': result.size,
                'Modified': datetime.fromtimestamp(result.modified_time).strftime("%Y-%m-%d %H:%M"),
                'Type': result.file_type,
                'Matches': len(result.matches) if result.matches else 0
            })
        
        df = pd.DataFrame(data)
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        with col1:
            file_type_filter = st.multiselect(
                "Filter by File Type",
                options=df['Type'].unique(),
                default=df['Type'].unique()
            )
        with col2:
            min_size_bytes = int(df['Size (bytes)'].min())
            max_size_bytes = int(df['Size (bytes)'].max())
            
            # Handle case where all files have the same size
            if min_size_bytes == max_size_bytes:
                st.info(f"All files have the same size: {self._format_size(min_size_bytes)}")
                size_range = (min_size_bytes, max_size_bytes)
            else:
                size_range = st.slider(
                    "Size Range (bytes)",
                    min_value=min_size_bytes,
                    max_value=max_size_bytes,
                    value=(min_size_bytes, max_size_bytes)
                )
        with col3:
            name_filter = st.text_input("Filter by name", placeholder="Enter text to filter filenames")
        
        # Apply filters
        filtered_df = df[df['Type'].isin(file_type_filter)]
        filtered_df = filtered_df[
            (filtered_df['Size (bytes)'] >= size_range[0]) & 
            (filtered_df['Size (bytes)'] <= size_range[1])
        ]
        if name_filter:
            filtered_df = filtered_df[filtered_df['Name'].str.contains(name_filter, case=False, na=False)]
        
        # Display table
        st.dataframe(
            filtered_df[['Name', 'Path', 'Size', 'Modified', 'Type', 'Matches']],
            use_container_width=True,
            hide_index=True
        )
        
        # Show content matches for content searches
        if any(r.matches for r in results):
            st.subheader("🔍 Content Matches")
            for i, result in enumerate(results):
                if result.matches:
                    with st.expander(f"📄 {result.name}"):
                        for match in result.matches[:10]:  # Show first 10 matches
                            st.code(match, language="text")
    
    def _render_results_charts(self, results: List[SearchResult]):
        """Render visualization charts"""
        if not results:
            st.info("No results to visualize")
            return
        
        # Prepare data
        df = pd.DataFrame([{
            'name': r.name,
            'size': r.size,
            'file_type': r.file_type,
            'modified': datetime.fromtimestamp(r.modified_time)
        } for r in results])
        
        col1, col2 = st.columns(2)
        
        with col1:
            # File type distribution
            type_counts = df['file_type'].value_counts().head(10)
            fig1 = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="File Types Distribution"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Size distribution
            fig2 = px.histogram(
                df,
                x='size',
                nbins=20,
                title="File Size Distribution"
            )
            fig2.update_layout(
                xaxis_title="File Size (bytes)",
                yaxis_title="Count"
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Timeline view
        df['date'] = df['modified'].dt.date
        daily_counts = df.groupby('date').size().reset_index(name='count')
        
        if len(daily_counts) > 1:
            fig3 = px.line(
                daily_counts,
                x='date',
                y='count',
                title="Files by Modification Date"
            )
            st.plotly_chart(fig3, use_container_width=True)
    
    def _render_export_options(self, results: List[SearchResult]):
        """Render export options"""
        if not results:
            st.info("No results to export")
            return
        
        st.subheader("💾 Export Results")
        
        # Prepare export data
        export_data = []
        for result in results:
            export_data.append({
                'Name': result.name,
                'Path': result.path,
                'Size': result.size,
                'Modified': datetime.fromtimestamp(result.modified_time).isoformat(),
                'Type': result.file_type,
                'Matches': '; '.join(result.matches) if result.matches else ''
            })
        
        df = pd.DataFrame(export_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV download
            csv = df.to_csv(index=False)
            st.download_button(
                label="📄 Download as CSV",
                data=csv,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON download
            import json
            json_data = json.dumps([result.to_dict() for result in results], indent=2)
            st.download_button(
                label="📋 Download as JSON",
                data=json_data,
                file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    def _render_search_history(self):
        """Render search history"""
        st.header("📜 Search History")
        
        history = st.session_state.search_history
        
        for i, search in enumerate(reversed(history[-10:])):  # Show last 10 searches
            with st.expander(
                f"{search['type']} search - {search['results_count']} results - "
                f"{search['timestamp'].strftime('%Y-%m-%d %H:%M')}"
            ):
                st.write(f"**Pattern:** {search['pattern']}")
                st.write(f"**Path:** {search['path']}")
                st.write(f"**Results:** {search['results_count']} files")
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '1MB', '500KB' to bytes"""
        if not size_str:
            return 0
        
        size_str = str(size_str).upper().strip()
        
        # Handle edge cases
        if size_str == "0" or size_str == "0B":
            return 0
        
        # Handle case where there's no number (just unit)
        if size_str in ['B', 'KB', 'MB', 'GB', 'TB']:
            return 0
        
        # Order matters! Check longer suffixes first
        multipliers = [
            ('TB', 1024**4),
            ('GB', 1024**3),
            ('MB', 1024**2),
            ('KB', 1024),
            ('B', 1),
        ]
        
        # Try to find matching suffix
        for suffix, multiplier in multipliers:
            if size_str.endswith(suffix):
                number_part = size_str[:-len(suffix)].strip()
                if not number_part:  # Handle case like "MB" without number
                    return 0
                try:
                    # Handle both integer and float inputs
                    number = float(number_part)
                    return int(number * multiplier)
                except ValueError:
                    raise ValueError(f"Invalid number '{number_part}' in size format")
        
        # If no suffix found, assume bytes
        try:
            return int(float(size_str))
        except ValueError:
            raise ValueError(f"Invalid size format: '{size_str}'. Expected format like '1MB', '500KB', etc.")
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"

def main():
    """Main entry point for the Streamlit app"""
    app = StreamlitApp()
    app.run()

def launch_streamlit():
    """Launch the Streamlit application programmatically"""
    try:
        # Get the path to this script
        script_path = os.path.abspath(__file__)
        
        # Launch Streamlit with this script
        cmd = [sys.executable, '-m', 'streamlit', 'run', script_path]
        subprocess.run(cmd, cwd=os.path.dirname(script_path))
    except FileNotFoundError:
        print("Error: Streamlit is not installed. Please install it with:")
        print("pip install streamlit")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
        sys.exit(0)

if __name__ == "__main__":
    # Simple and safe launch logic
    if len(sys.argv) > 1 and sys.argv[1] == "--launch":
        # Explicit launch flag - launch streamlit
        launch_streamlit()
    else:
        # Default behavior - just run the main app
        # This works both when run directly by streamlit and when imported
        main()
