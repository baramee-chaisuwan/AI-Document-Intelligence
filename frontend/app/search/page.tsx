import AppLayout from "@/components/layout/AppLayout";
import SearchBox from "@/components/search/SearchBox";

export default function SearchPage() {

    return (

        <AppLayout
            title="AI Search"
            description="Semantic search for candidates using AI embeddings"
        >

            <SearchBox />

        </AppLayout>

    );

}