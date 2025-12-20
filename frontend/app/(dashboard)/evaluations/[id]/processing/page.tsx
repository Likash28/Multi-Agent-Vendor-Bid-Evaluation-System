import { ProcessingView } from '@/components/processing/processing-view';

interface ProcessingPageProps {
  params: {
    id: string;
  };
}

export default function ProcessingPage({ params }: ProcessingPageProps) {
  return <ProcessingView evaluationId={params.id} />;
}
